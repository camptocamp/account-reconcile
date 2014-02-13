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

import openerp.tests.common as common


def prepare_move(test, product_ref, quantity):
    return {'name': '/',
            'product_id': test.ref(product_ref),
            'product_uom': test.ref('product.product_uom_unit'),
            'product_qty': quantity,
            'location_id': test.ref('stock.stock_location_14'),
            'location_dest_id': test.ref('stock.stock_location_7'),
            }


def prepare_pack(test):
    return {
            }


def create_pack(test, pack, moves):
    pack_id = test.registry('stock.tracking').create(
        test.cr, test.uid, pack)
    for move in moves:
        test.registry('stock.move').create(
            test.cr, test.uid, dict(move, tracking_id=pack_id))
    return pack_id


class test_automatic_group(common.TransactionCase):

    def setUp(self):
        super(test_automatic_group, self).setUp()
        self.pack_id_1 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 10),
             prepare_move(self, 'product.product_product_20', 10),
             ])

        self.pack_id_2 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_31', 5),
             prepare_move(self, 'product.product_product_20', 10),
             ])

        self.pack_id_3 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 10),
             prepare_move(self, 'product.product_product_20', 10),
             ])

        self.pack_id_4 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 5),
             prepare_move(self, 'product.product_product_20', 10),
             ])

        self.pack_id_5 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 5),
             prepare_move(self, 'product.product_product_20', 10),
             prepare_move(self, 'product.product_product_24', 1),
             ])

        self.pack_id_6 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_26', 5),
             ])

        self.pack_id_7 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 10),
             prepare_move(self, 'product.product_product_20', 10),
             ])

        self.pack_id_8 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_31', 5),
             prepare_move(self, 'product.product_product_20', 10),
             ])

        self.all_pack_ids = [self.pack_id_1,
                             self.pack_id_2,
                             self.pack_id_3,
                             self.pack_id_4,
                             self.pack_id_5,
                             self.pack_id_6,
                             self.pack_id_7,
                             self.pack_id_8,
                             ]
        self.Dispatch = self.registry('picking.dispatch')
        self.existing_dispatch_ids = self.Dispatch.search(
            self.cr, self.uid, [])

    def _call_wizard(self, options):
        Wizard = self.registry('picking.dispatch.grouper')
        Dispatch = self.registry('picking.dispatch')
        wizard_id = Wizard.create(self.cr, self.uid, options)
        wizard = Wizard.browse(self.cr, self.uid, wizard_id)
        dispatch_ids = Wizard._group_packs(self.cr, self.uid, wizard,
                                           self.all_pack_ids)
        return Dispatch.browse(self.cr, self.uid, dispatch_ids)

    def test_group_one(self):
        """ Without grouping packs and without max.

        Should generate 1 dispatch.

        """
        options = {'max_pack': 0,
                   'only_product_ids': [],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 1)
        self.assertEquals(len(dispatchs[0].move_ids), 16)

    def test_group_max(self):
        """ Without grouping packs but with a max limit.

        We set a limit of 3 packs per dispatch, it should generate 5
        dispatchs.

        """
        options = {'max_pack': 3,
                   'only_product_ids': [],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 3)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 16)

    def test_group_by_content(self):
        """ With grouping packs, no grouping of leftovers and no size limit.

        Given the input packs, we should have dispatchs with identical
        content as following:

            pack 1, pack 3, pack 7

            pack 2, pack 8

            pack 4

            pack 5

            pack 6

        """
        options = {'max_pack': 0,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 5)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 16)

    def test_group_by_content_with_leftovers(self):
        """ With grouping packs, grouping of leftovers and no max limit.

        Given the input packs, we should have dispatchs with identical
        content as following:

            pack 1, pack 3, pack 7

            pack 2, pack 8

            pack 4, pack 5, pack 6 (leftovers)

        """
        options = {'max_pack': 0,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': True,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 3)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 16)

    def test_group_by_content_with_max(self):
        """ With grouping packs, no grouping of leftovers and a max limit of 2.

        Given the input packs, we should have dispatchs with identical
        content as following:

            pack 1, pack 3

            pack 7

            pack 2, pack 8

            pack 4

            pack 5

            pack 6

        """
        options = {'max_pack': 2,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 6)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 16)

    def test_group_by_content_with_leftovers_and_max(self):
        """ With grouping packs, grouping of leftovers and max limit of 2.

        Given the input packs, we should have dispatchs with identical
        content as following:

            pack 1, pack 3,

            pack 2, pack 8

            pack 4, pack 5 (leftovers)

            pack 6, pack 7 (leftovers)

        """
        options = {'max_pack': 2,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': True,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 4)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 16)

    def test_group_filter(self):
        """ Without grouping packs, no limit, filter on a group of products.

        Filter on products
             'product.product_product_33'
             'product.product_product_20'

        We should have 4 packs in 1 dispatch.

        """
        pr33 = self.ref('product.product_product_33')
        pr20 = self.ref('product.product_product_20')
        options = {'max_pack': 0,
                   'only_product_ids': [(6, 0, [pr33, pr20])],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 1)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 8)

    def test_group_filter_grouping(self):
        """ With grouping packs, no limit, filter on a group of products.

        Filter on products
             'product.product_product_33'
             'product.product_product_20'

        We should have 4 packs in 2 dispatch.

        """
        pr33 = self.ref('product.product_product_33')
        pr20 = self.ref('product.product_product_20')
        options = {'max_pack': 0,
                   'only_product_ids': [(6, 0, [pr33, pr20])],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 2)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 8)

    def test_group_filter_grouping_max(self):
        """ With grouping packs, a limit, filter on a group of products.

        Filter on products
             'product.product_product_33'
             'product.product_product_20'

        With a limit of 2.

        We should have 4 packs in 3 dispatch.

        """
        pr33 = self.ref('product.product_product_33')
        pr20 = self.ref('product.product_product_20')
        options = {'max_pack': 2,
                   'only_product_ids': [(6, 0, [pr33, pr20])],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 3)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 8)

    def test_group_filter_grouping_max_leftovers(self):
        """ With grouping packs and leftovers, a limit, filter on a group of products.

        Filter on products
             'product.product_product_33'
             'product.product_product_20'

        With a limit of 2.

        We should have 4 packs in 2 dispatchs (the leftover of first group
        will be grouped with the standalone pack).

        """
        pr33 = self.ref('product.product_product_33')
        pr20 = self.ref('product.product_product_20')
        options = {'max_pack': 2,
                   'only_product_ids': [(6, 0, [pr33, pr20])],
                   'group_by_content': True,
                   'group_leftovers': True,
                   }
        dispatchs = self._call_wizard(options)
        self.assertEquals(len(dispatchs), 2)
        moves = [m for dispatch in dispatchs for m in dispatch.move_ids]
        self.assertEquals(len(moves), 8)
