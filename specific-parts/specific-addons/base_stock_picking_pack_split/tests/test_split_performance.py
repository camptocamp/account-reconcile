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

"""
No assertion, used to measure the time the split takes
in order to improve the duration of the operation.
"""

import time
from contextlib import contextmanager
import openerp.tests.common as common


class test_split_performance(common.TransactionCase):
    """ Test the performance

    """

    def _create_picking(self, number_of_products):
        cr, uid = self.cr, self.uid
        line = {'name': '/',
                'product_id': self.ref('product.product_product_33'),
                'product_uom': self.ref('product.product_uom_unit'),
                'product_qty': number_of_products,
                'location_id': self.ref('stock.stock_location_14'),
                'location_dest_id': self.ref('stock.stock_location_7'),
                }
        picking_id = self.Picking.create(
            cr, uid,
            {'partner_id': self.ref('base.res_partner_12'),
             'move_lines': [(0, 0, line)],
             'type': 'out'})
        return self.Picking.browse(cr, uid, picking_id)

    def setUp(self):
        super(test_split_performance, self).setUp()

        self.Move = self.registry('stock.move')
        self.Picking = self.registry('stock.picking')

    @contextmanager
    def _benchmark(self):
        start = time.time()
        yield
        end = time.time()
        print "%0.3f seconds" % (end - start)

    def test_prepare_packs_10_products(self):
        """ Picking with 10 products """
        picking = self._create_picking(10)

        with self._benchmark():
            picking.prepare_packs(max_qty=1)

    def test_prepare_packs_100_products(self):
        """ Picking with 100 products """
        picking = self._create_picking(100)

        with self._benchmark():
            picking.prepare_packs(max_qty=1)

    def test_prepare_packs_1000_products(self):
        """ Picking with 1000 products """
        picking = self._create_picking(1000)

        with self._benchmark():
            picking.prepare_packs(max_qty=1)

    def test_prepare_packs_10_pickings(self):
        """ 10 Picking with 3 products """
        cr, uid = self.cr, self.uid
        picking_ids = []
        for _ in xrange(10):
            picking_ids.append(self._create_picking(3).id)

        with self._benchmark():
            self.Picking.prepare_packs(cr, uid, picking_ids, max_qty=1)

    def test_prepare_packs_100_pickings(self):
        """ 100 Picking with 3 products """
        cr, uid = self.cr, self.uid
        picking_ids = []
        for _ in xrange(100):
            picking_ids.append(self._create_picking(3).id)

        with self._benchmark():
            self.Picking.prepare_packs(cr, uid, picking_ids, max_qty=1)

    def test_prepare_packs_1000_pickings(self):
        """ 1000 Picking with 3 products """
        cr, uid = self.cr, self.uid
        picking_ids = []
        for _ in xrange(1000):
            picking_ids.append(self._create_picking(3).id)

        with self._benchmark():
            self.Picking.prepare_packs(cr, uid, picking_ids, max_qty=1)
