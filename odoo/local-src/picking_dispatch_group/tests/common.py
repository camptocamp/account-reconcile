# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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


def prepare_move(test, product_ref, quantity):
    return {'name': '/',
            'product_id': test.ref(product_ref),
            'product_uom': test.ref('product.product_uom_unit'),
            'product_qty': quantity,
            'location_id': test.ref('stock.stock_location_14'),
            'location_dest_id': test.ref('stock.stock_location_7'),
            }


def prepare_pack(test):
    return {}


def create_pack(test, pack, moves):
    pack_id = test.registry('stock.tracking').create(
        test.cr, test.uid, pack)
    for move in moves:
        test.registry('stock.move').create(
            test.cr, test.uid, dict(move, tracking_id=pack_id))
    return pack_id
