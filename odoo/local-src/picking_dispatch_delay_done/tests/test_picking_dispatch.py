# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.exceptions import UserError
from openerp.tests import TransactionCase

from mock import patch


class TestPickingDispatch(TransactionCase):

    def setUp(self):
        super(TestPickingDispatch, self).setUp()

        self.dispatch_model = self.env['picking.dispatch']
        self.wizard_model = self.env['picking.dispatch.delayed.done']
        product_model = self.env['product.product']

        product1 = product_model.create({'name': 'Unittest P1'})
        product2 = product_model.create({'name': 'Unittest P2'})

        self.picking = self.create_simple_picking([product1.id, product2.id])
        self.picking.action_confirm()

        self.dispatch1 = self.dispatch_model.create({
            'state': 'progress',
            'picker_id': self.env.uid,
            'move_ids': [(4, self.picking.move_lines[0].id)]
        })

        self.dispatch2 = self.dispatch_model.create({
            'state': 'progress',
            'picker_id': self.env.uid,
            'move_ids': [(4, self.picking.move_lines[1].id)]
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
            active_ids=[self.dispatch1.id, self.dispatch2.id]
        ).create({})

        wizard.delayed_done()
        self.assertEqual('delayed_done', self.dispatch1.state)
        self.assertEqual('delayed_done', self.dispatch2.state)
        self.assertEqual('confirmed', self.picking.move_lines[0].state)
        self.assertEqual('confirmed', self.picking.move_lines[1].state)

        # Simulate cron but without commit.
        with patch.object(self.env.cr, "commit") as mock_commit:
            self.dispatch_model._scheduler_delayed_done()
            self.assertEqual(2, mock_commit.call_count)

        self.assertEqual('done', self.dispatch1.state)
        self.assertEqual('done', self.dispatch2.state)
        self.assertEqual('done', self.picking.move_lines[0].state)
        self.assertEqual('done', self.picking.move_lines[1].state)

    def test_wizard_wrong_state(self):
        self.dispatch1.state = 'assigned'
        wizard = self.wizard_model.with_context(
            active_ids=[self.dispatch1.id, self.dispatch2.id]
        ).create({})

        with self.assertRaises(UserError):
            wizard.delayed_done()
