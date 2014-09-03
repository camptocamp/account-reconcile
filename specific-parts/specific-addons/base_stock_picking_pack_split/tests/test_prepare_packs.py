# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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


class test_prepare_packs(common.TransactionCase):
    """ Test the method to prepare packs
    Setting a max number of product per pack
    """

    def setUp(self):
        super(test_prepare_packs, self).setUp()
        cr, uid = self.cr, self.uid

        self.Move = self.registry('stock.move')
        self.Picking = self.registry('stock.picking')

        self.picking_out_1_id = self.Picking.create(
            cr, uid,
            {'partner_id': self.ref('base.res_partner_12'),
             'type': 'out'})

        self.Move.create(
            cr, uid,
            {'name': '/',
             'picking_id': self.picking_out_1_id,
             'product_id': self.ref('product.product_product_33'),
             'product_uom': self.ref('product.product_uom_unit'),
             'product_qty': 10,
             'location_id': self.ref('stock.stock_location_14'),
             'location_dest_id': self.ref('stock.stock_location_7'),
             })

        self.Move.create(
            cr, uid,
            {'name': '/',
             'picking_id': self.picking_out_1_id,
             'product_id': self.ref('product.product_product_33'),
             'product_uom': self.ref('product.product_uom_unit'),
             'product_qty': 8,
             'location_id': self.ref('stock.stock_location_14'),
             'location_dest_id': self.ref('stock.stock_location_7'),
             })

        self.Move.create(
            cr, uid,
            {'name': '/',
             'picking_id': self.picking_out_1_id,
             'product_id': self.ref('product.product_product_33'),
             'product_uom': self.ref('product.product_uom_unit'),
             'product_qty': 6,
             'location_id': self.ref('stock.stock_location_14'),
             'location_dest_id': self.ref('stock.stock_location_7'),
             })

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
        cr, uid = self.cr, self.uid
        picking = self.Picking.browse(cr, uid, self.picking_out_1_id)
        picking.prepare_packs(max_qty=3)

        moves = picking.move_lines

        # There is 9 moves
        assert len(moves) == 9

        packs = list(set([m.tracking_id for m in moves]))
        # There is 8 packs
        assert len(packs) == 8

        # There is no more than 3 product per pack
        assert [p.id for p in packs
                if sum(m.product_qty for m in p.move_ids) <= 3]
