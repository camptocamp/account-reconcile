# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from mock import patch, ANY, MagicMock

from ..picking.exporter import export_picking_tracking_done
from .common import recorder, QoQaTransactionCase


class TestExportPicking(QoQaTransactionCase):

    def setUp(self):
        super(TestExportPicking, self).setUp()

        self.mock_delay_export = MagicMock()
        self.patch_delay = patch(
            'openerp.addons.connector_qoqa.picking'
            '.exporter.export_picking_tracking_done.delay',
            new=self.mock_delay_export
        )
        self.patch_delay.start()

        stock_loc = self.ref('stock.stock_location_stock')
        customer_loc = self.ref('stock.stock_location_customers')

        self.carrier_partner = self.env['res.partner'].create({
            'name': 'Unittest carrier partner'
        })

        self.customer_partner = self.env['res.partner'].create({
            'name': 'Unittest customer partner',
        })

        self.carrier = self.env['delivery.carrier'].create({
            'partner_id': self.carrier_partner.id,
            'name': 'Unittest carrier',
        })

        self.product_1 = self.env['product.product'].create({
            'name': 'Unittest P1'
        })
        self.create_bindind_no_export(
            'qoqa.product.product', self.product_1.id, '100011'
        )

        self.sale = self.env['sale.order'].create({
            'partner_id': self.customer_partner.id,
            'partner_invoice_id': self.customer_partner.id,
            'partner_shipping_id': self.customer_partner.id,
            'order_line': [(0, 0, {
                'name': self.product_1.name,
                'product_id': self.product_1.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product_1.uom_id.id,
            })],
            'pricelist_id': self.env.ref('product.list0').id,
        })

        self.packacking = self.env['product.packaging'].create({
            'name': 'colis < 1kg',
            'qoqa_id': 7,
        })

        procurement = self.env['procurement.order'].create({
            "name": "Unittest P1 procurement",
            "product_id": self.product_1.id,
            'product_uom': self.product_1.uom_id.id,
            'product_qty': 1,
            "sale_line_id": self.sale.order_line[0].id
        })

        self.picking = self.env['stock.picking'].create({
            'carrier_id': self.carrier.id,
            'picking_type_id': self.ref('stock.picking_type_out'),
            'location_id': stock_loc,
            'location_dest_id': customer_loc,
            'move_lines': [
                (0, 0, {
                    'name': 'Test move',
                    'procurement_id': procurement.id,
                    'product_id': self.product_1.id,
                    'product_uom': self.ref('product.product_uom_unit'),
                    'product_uom_qty': 5,
                    'location_id': stock_loc,
                    'location_dest_id': customer_loc
                })
            ]
        })

    def tearDown(self):
        self.patch_delay.stop()

    def _check_json_body(self, path, query_json, saved_json):
        self.assertEqual(['shipping_packages'], query_json.keys())
        packages = query_json['shipping_packages']
        self.assertEqual(1, len(packages))

        expected = {
            'tracking_number': 'PKG_1',
            'shipping_package_type_id': '7',
            'shipping_package_items_attributes': [{
                'variation_id': '100011',
                'quantity': 5,
            }]
        }
        self.assertEqual(expected, packages[0])
        return True

    def create_bindind_no_export(self, model_name, openerp_id, qoqa_id=None):
        return self.env[model_name].with_context(
            connector_no_export=True
        ).create({
            'backend_id': self.backend_record.id,
            'openerp_id': openerp_id,
            'qoqa_id': qoqa_id
        })

    def set_picking_done(self, package_ref=None):
        self.picking.action_assign()
        for op in self.picking.pack_operation_ids:
            op.qty_done = op.product_qty

        if package_ref:
            package_id = self.picking.put_in_pack()
            package = self.env['stock.quant.package'].browse(package_id)
            package.name = package_ref
            package.packaging_id = self.packacking.id

        self.picking.do_transfer()
        picking_binding = self.env['qoqa.stock.picking'].search([
            ('openerp_id', '=', self.picking.id)
        ])
        self.assertEqual(1, len(picking_binding))
        return picking_binding

    def test_picking_done__not_qoqa_sale(self):
        """ Test that binding is created and export scheduled
        """
        self.assertEqual(0, self.env['qoqa.stock.picking'].search_count([]))
        self.picking.do_transfer()
        self.assertEqual('done', self.picking.state)
        self.assertEqual(0, self.env['qoqa.stock.picking'].search_count([]))

        self.assertEqual(0, self.mock_delay_export.call_count)

    def test_picking_done__qoqa_sale(self):
        """ Test that binding is created and export scheduled
        """
        self.env['qoqa.sale.order'].create({
            'backend_id': self.backend_record.id,
            'openerp_id': self.sale.id,
            'qoqa_id': '10',
        })

        self.assertEqual(0, self.env['qoqa.stock.picking'].search_count([]))
        self.picking.do_transfer()
        self.assertEqual('done', self.picking.state)
        self.assertEqual(1, self.env['qoqa.stock.picking'].search_count([]))

        picking_binding = self.env['qoqa.stock.picking'].search([])
        self.assertEqual(self.picking, picking_binding.openerp_id)
        self.assertEqual(self.backend_record, picking_binding.backend_id)

        self.mock_delay_export.assert_called_once_with(
            ANY, 'qoqa.stock.picking', picking_binding.id
        )

    def test_export_picking(self):
        self.create_bindind_no_export(
            'qoqa.sale.order', self.sale.id, '10'
        )
        picking_binding = self.set_picking_done(package_ref="PKG_1")

        vcr_name = 'test_export_picking'
        match_on = recorder.match_on + ('json_body',)
        with recorder.use_cassette(vcr_name, match_on=match_on) as cassette:
            export_picking_tracking_done(
                self.session, 'qoqa.stock.picking', picking_binding.id
            )
            self.assertEqual(len(cassette.requests), 1)

            self.assertEqual(True, picking_binding.exported)
