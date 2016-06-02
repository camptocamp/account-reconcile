# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import TransactionCase


class TestStockPicking(TransactionCase):

    def setUp(self):
        super(TestStockPicking, self).setUp()

        # Need to disable all sale exception
        exceptions = self.env['sale.exception'].search([])
        exceptions.write({'active': False})

    def test_sale_creation_date(self):
        # Test that sale_create_date is copied from sale_order.create_date
        test_product = self.env['product.product'].create({
            'name': 'Unittest product'
        })

        partner = self.env['res.partner'].create({'name': 'Test'})

        self.assertEqual(0, self.env['stock.picking'].search_count([
            ('move_lines.product_id', '=', test_product.id)
        ]))
        sale = self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'name': test_product.name,
                'product_id': test_product.id,
                'product_uom_qty': 1.0,
                'product_uom': test_product.uom_id.id,
            })],
        })

        sale.action_confirm()
        picking = self.env['stock.picking'].search([
            ('move_lines.product_id', '=', test_product.id)
        ])
        self.assertEqual(1, len(picking))

        self.assertEqual(sale.create_date, picking.sale_create_date)

        # Just for check that sale_create_date is no more related
        self.env.cr.execute(
            "UPDATE sale_order SET create_date=create_date - INTERVAL '1 DAY'"
        )
        sale.invalidate_cache()
        self.assertNotEqual(sale.create_date, picking.sale_create_date)
