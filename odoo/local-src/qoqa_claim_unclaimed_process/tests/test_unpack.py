# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp.tests.common import SavepointCase


class TestUnpack(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestUnpack, cls).setUpClass()
        cls.product_model = cls.env['product.product']
        cls.picking_model = cls.env['stock.picking']
        cls.move_model = cls.env['stock.move']

        cls.partner_agrolite_id = cls.env.ref('base.res_partner_2').id
        cls.partner_delta_id = cls.env.ref('base.res_partner_4').id
        cls.picking_type_in = cls.env.ref('stock.picking_type_in').id
        cls.picking_type_out = cls.env.ref('stock.picking_type_out').id
        cls.supplier_location = cls.env.ref(
            'stock.stock_location_suppliers'
        ).id
        cls.stock_location = cls.env.ref('stock.stock_location_stock').id
        cls.customer_location = cls.env.ref(
            'stock.stock_location_customers'
        ).id

        cls.product_1 = cls.product_model.create({
            'name': 'Product 1',
            'type': 'product',
            'categ_id': 1,
        })
        cls.product_2 = cls.product_model.create({
            'name': 'Product 2',
            'type': 'product',
            'categ_id': 1,
        })

        cls.picking_in = cls.picking_model.create({
            'partner_id': cls.partner_delta_id,
            'picking_type_id': cls.picking_type_in,
            'location_id': cls.supplier_location,
            'location_dest_id': cls.stock_location})
        cls.move_model.create({
            'name': cls.product_2.name,
            'product_id': cls.product_2.id,
            'product_uom_qty': 30,
            'product_uom': cls.product_2.uom_id.id,
            'picking_id': cls.picking_in.id,
            'location_id': cls.supplier_location,
            'location_dest_id': cls.stock_location})
        cls.move_model.create({
            'name': cls.product_1.name,
            'product_id': cls.product_1.id,
            'product_uom_qty': 40,
            'product_uom': cls.product_1.uom_id.id,
            'picking_id': cls.picking_in.id,
            'location_id': cls.supplier_location,
            'location_dest_id': cls.stock_location})
        cls.picking_in.action_confirm()
        cls.picking_in.action_assign()
        cls.pack_obj = cls.env['stock.quant.package']
        cls.pack1 = cls.pack_obj.create({'name': 'PACKINOUTTEST1'})
        cls.picking_in.pack_operation_ids[0].result_package_id = cls.pack1
        cls.picking_in.pack_operation_ids[0].product_qty = 30
        cls.picking_in.pack_operation_ids[1].result_package_id = cls.pack1
        cls.picking_in.pack_operation_ids[1].product_qty = 40
        cls.picking_in.do_transfer()

    def test_unpack(self):
        picking_out = self.picking_model.create({
            'partner_id': self.partner_agrolite_id,
            'picking_type_id': self.picking_type_out,
            'location_id': self.stock_location,
            'location_dest_id': self.customer_location})
        picking_out.action_confirm()
        picking_out.pack_operation_pack_ids = [(0, 0, {
            'package_id': self.pack1.id,
            'location_id': self.stock_location,
            'location_dest_id': self.customer_location,
        })]
        self.assertEqual(len(picking_out.pack_operation_ids), 1)
        pack_id = self.pack1.id
        self.pack1.unpack()
        # Check if pack is deleted
        self.assertEqual(len(self.pack_obj.search([('id', '=', pack_id)])), 0)
        # Check picking state to be available
        self.assertEqual(picking_out.state, 'assigned')
        # Make sure picking contains all the objects
        self.assertEqual(len(picking_out.pack_operation_ids), 2)
        self.assertEqual(len(picking_out.pack_operation_pack_ids), 0)
        self.assertEqual(len(picking_out.pack_operation_product_ids), 2)
        self.assertEqual(
            sorted(picking_out.pack_operation_product_ids.mapped(
                "product_id"
            ).ids),
            sorted([self.product_2.id, self.product_1.id]),
        )
        self.assertEqual(
            sorted(picking_out.pack_operation_product_ids.mapped(
                "product_qty"
            )),
            sorted([30.0, 40.0]),
        )
