# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014-2016 Camptocamp SA
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

import os
import time
from contextlib import contextmanager

import unittest

import openerp.tests.common as common


class TestSplitPerformance(common.TransactionCase):
    """ Test the performance

    """

    def _create_picking(self, number_of_products):
        line = {'name': '/',
                'product_id': self.product_id,
                'product_uom': self.ref('product.product_uom_unit'),
                'product_uom_qty': number_of_products,
                'location_id': self.loc_src_id,
                'location_dest_id': self.ref('stock.stock_location_customers')}
        picking = self.env['stock.picking'].create(
            {'partner_id': self.ref('base.res_partner_12'),
             'move_lines': [(0, 0, line)],
             'picking_type_id': self.ref('stock.picking_type_out'),
             'location_id': self.loc_src_id,
             'location_dest_id': self.ref('stock.stock_location_customers')})
        picking.action_confirm()
        picking.action_assign()
        return picking

    def setUp(self):
        super(TestSplitPerformance, self).setUp()
        self.loc_src_id = self.ref('stock.stock_location_stock')
        self.product_id = self.ref('product.product_product_48')
        inventory = self.env['stock.inventory'].create({
            'name': 'Test',
            'product_id': self.product_id,
            'filter': 'product'})
        inventory.prepare_inventory()
        self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.product_id,
            'product_qty': 10000,
            'location_id': self.loc_src_id})
        inventory.action_done()

    @contextmanager
    def _benchmark(self):
        start = time.time()
        yield
        end = time.time()
        print "%0.3f seconds" % (end - start)

    @unittest.skipIf(os.environ.get('TRAVIS'),
                     'Skipping time-consuming tests on Travis CI')
    def test_prepare_packs_10_products(self):
        """ Picking with 10 products """
        picking = self._create_picking(10)

        with self._benchmark():
            picking.prepare_packs(max_qty=1)

    @unittest.skipIf(os.environ.get('TRAVIS'),
                     'Skipping time-consuming tests on Travis CI')
    def test_prepare_packs_100_products(self):
        """ Picking with 100 products """
        picking = self._create_picking(100)

        with self._benchmark():
            picking.prepare_packs(max_qty=1)

    @unittest.skipIf(os.environ.get('TRAVIS'),
                     'Skipping time-consuming tests on Travis CI')
    def test_prepare_packs_1000_products(self):
        """ Picking with 1000 products """
        picking = self._create_picking(1000)

        with self._benchmark():
            picking.prepare_packs(max_qty=1)

    @unittest.skipIf(os.environ.get('TRAVIS'),
                     'Skipping time-consuming tests on Travis CI')
    def test_prepare_packs_10_pickings(self):
        """ 10 Picking with 3 products """
        pickings = self.env['stock.picking']
        for _ in xrange(10):
            pickings |= self._create_picking(3)

        with self._benchmark():
            pickings.prepare_packs(max_qty=1)

    @unittest.skipIf(os.environ.get('TRAVIS'),
                     'Skipping time-consuming tests on Travis CI')
    def test_prepare_packs_100_pickings(self):
        """ 100 Picking with 3 products """
        pickings = self.env['stock.picking']
        for _ in xrange(100):
            pickings |= self._create_picking(3)

        with self._benchmark():
            pickings.prepare_packs(max_qty=1)

    @unittest.skipIf(os.environ.get('TRAVIS'),
                     'Skipping time-consuming tests on Travis CI')
    def test_prepare_packs_1000_pickings(self):
        """ 1000 Picking with 3 products """
        pickings = self.env['stock.picking']
        for _ in xrange(1000):
            pickings |= self._create_picking(3)

        with self._benchmark():
            pickings.prepare_packs(max_qty=1)
