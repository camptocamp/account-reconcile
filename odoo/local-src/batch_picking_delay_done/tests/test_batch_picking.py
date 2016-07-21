# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.exceptions import UserError
from openerp.tests import TransactionCase

from mock import patch


class TestStockBatchPicking(TransactionCase):

    def setUp(self):
        super(TestStockBatchPicking, self).setUp()

        self.batch_model = self.env['stock.batch.picking']
        self.wizard_model = self.env['stock.batch.picking.delayed.done']
        product_model = self.env['product.product']

        product1 = product_model.create({'name': 'Unittest P1'})
        product2 = product_model.create({'name': 'Unittest P2'})
        self.wh_main = self.browse_ref('stock.warehouse0')

        # Add products in stock
        inventory = self.env['stock.inventory'].create({
            'name': 'Add test products',
            'location_id': self.ref('stock.stock_location_locations'),
            'filter': 'partial'
        })
        inventory.prepare_inventory()
        for product in [product1, product2]:
            self.env['stock.inventory.line'].create({
                'inventory_id': inventory.id,
                'product_id': product.id,
                'location_id': self.wh_main.lot_stock_id.id,
                'product_qty': 10.0
            })
        inventory.action_done()

        self.picking = self.create_simple_picking([product1.id])
        self.picking.action_confirm()

        self.picking2 = self.create_simple_picking([product2.id])
        self.picking2.action_confirm()

        self.batch1 = self.batch_model.create({
            'picking_ids': [(4, self.picking.id)]
        })

        self.batch2 = self.batch_model.create({
            'picking_ids': [(4, self.picking2.id)]
        })

    def create_simple_picking(self, product_ids):
        stock_loc = self.ref('stock.stock_location_stock')
        customer_loc = self.ref('stock.stock_location_customers')

        return self.env['stock.picking'].create({
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': stock_loc,
            'location_dest_id': customer_loc,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'product_id': product_id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 1,
                    'location_id': stock_loc,
                    'location_dest_id': customer_loc
                }) for product_id in product_ids
                ]
        })

    def test_delay_done_workflow(self):

        # No active_ids
        wrong_wizard = self.wizard_model.create({})
        with self.assertRaises(UserError):
            wrong_wizard.delayed_done()

        wizard = self.wizard_model.with_context(
            active_ids=[self.batch1.id, self.batch2.id]
        ).create({})

        wizard.delayed_done()
        self.assertEqual('delayed_done', self.batch1.state)
        self.assertEqual('delayed_done', self.batch2.state)
        self.assertEqual('confirmed', self.picking.state)
        self.assertEqual('confirmed', self.picking.state)

        # Simulate cron but without commit.
        with patch.object(self.env.cr, "commit") as mock_commit:
            self.batch_model._scheduler_delayed_done()
            self.assertEqual(2, mock_commit.call_count)

        self.assertEqual('done', self.batch1.state)
        self.assertEqual('done', self.batch2.state)
        self.assertEqual('done', self.picking.state)
        self.assertEqual('done', self.picking2.state)

    def test_wizard_wrong_state(self):
        self.batch1.state = 'cancel'
        wizard = self.wizard_model.with_context(
            active_ids=[self.batch1.id, self.batch2.id]
        ).create({})

        with self.assertRaises(UserError):
            wizard.delayed_done()
