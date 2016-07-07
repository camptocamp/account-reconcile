# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013-2016 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp.tests.common as common


class TestPreparePacks(common.TransactionCase):
    """ Test the method to prepare packs
    Setting a max number of product per pack
    """

    def setUp(self):
        super(TestPreparePacks, self).setUp()

        self.Move = self.env['stock.move']
        self.Picking = self.env['stock.picking']

        self.picking_out_1 = self.Picking.create(
            {'partner_id': self.ref('base.res_partner_12'),
             'picking_type_id': self.ref('stock.picking_type_out'),
             'location_id': self.ref('stock.stock_location_stock'),
             'location_dest_id': self.ref('stock.stock_location_customers')})

        # need different products as operations groupe by product
        self.Move.create(
            {'name': '/',
             'picking_id': self.picking_out_1.id,
             'product_id': self.ref('product.product_product_12'),
             'product_uom': self.ref('product.product_uom_unit'),
             'product_uom_qty': 10,
             'location_id': self.ref('stock.stock_location_stock'),
             'location_dest_id': self.ref('stock.stock_location_customers')})

        self.Move.create(
            {'name': '/',
             'picking_id': self.picking_out_1.id,
             'product_id': self.ref('product.product_product_10'),
             'product_uom': self.ref('product.product_uom_unit'),
             'product_uom_qty': 8,
             'location_id': self.ref('stock.stock_location_stock'),
             'location_dest_id': self.ref('stock.stock_location_customers')})

        self.Move.create(
            {'name': '/',
             'picking_id': self.picking_out_1.id,
             'product_id': self.ref('product.product_product_24'),
             'product_uom': self.ref('product.product_uom_unit'),
             'product_uom_qty': 6,
             'location_id': self.ref('stock.stock_location_stock'),
             'location_dest_id': self.ref('stock.stock_location_customers')})
        self.picking_out_1.action_confirm()
        self.picking_out_1.action_assign()

    def test_00_prepare_packs(self):
        """ Check pack preparation

        Preparing packs of 3 objects from 3 move liens:

        - A: 10 items
        - B: 8 items
        - C: 6 items

        Resulting packs should be:

        3x 3A
        1x 1A + 2B
        2x 3B
        2x 3C

        """
        self.picking_out_1.prepare_packs(max_qty=3)

        ops = self.picking_out_1.pack_operation_product_ids

        # There is 9 operations
        assert len(ops) == 9

        packs = list(set([op.result_package_id for op in ops]))
        # There is 8 packs
        assert len(packs) == 8

        def qty_in_pack(pack):
            ops = self.env['stock.pack.operation'].search(
                [('result_package_id', '=', pack.id)])
            return sum(op.product_qty for op in ops)
        # There is no more than 3 product per pack
        assert all(qty_in_pack(pack) <= 3 for pack in packs)
