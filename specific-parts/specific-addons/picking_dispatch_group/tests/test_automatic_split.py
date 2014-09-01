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
from .common import prepare_move, prepare_pack, create_pack


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

        self.pack_id_9 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_31', 1),
             ])

        self.pack_id_10 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_31', 1),
             ])

        self.pack_id_11 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_31', 1),
             ])

        self.all_pack_ids = [self.pack_id_1,
                             self.pack_id_2,
                             self.pack_id_3,
                             self.pack_id_4,
                             self.pack_id_5,
                             self.pack_id_6,
                             self.pack_id_7,
                             self.pack_id_8,
                             self.pack_id_9,
                             self.pack_id_10,
                             self.pack_id_11,
                             ]
        self.Dispatch = self.registry('picking.dispatch')
        self.existing_dispatch_ids = self.Dispatch.search(
            self.cr, self.uid, [])

    def _call_wizard(self, options):
        Wizard = self.registry('picking.dispatch.group')
        Dispatch = self.registry('picking.dispatch')
        wizard_id = Wizard.create(self.cr, self.uid, options)
        wizard = Wizard.browse(self.cr, self.uid, wizard_id)
        dispatch_ids = Wizard._group_packs(self.cr, self.uid, wizard,
                                           self.all_pack_ids)
        return Dispatch.browse(self.cr, self.uid, dispatch_ids)

    def test_all_off(self):
        """ Without grouping packs and without limit.

        Should generate 1 dispatch.

        """
        options = {'pack_limit': 0,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 1)
        self.assertEquals(len(dispatches[0].move_ids), 19)

    def test_limit(self):
        """ Without grouping packs but with a limit.

        We set a limit of 3 packs per dispatch, it should generate 4
        dispatches.

        """
        options = {'pack_limit': 3,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 4)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 19)

    def test_group(self):
        """ With grouping packs, no grouping of leftovers and no size limit.

        Given the input packs, we should have dispatches with identical
        content as following:

            pack 1, pack 3, pack 7

            pack 2, pack 8

            pack 4

            pack 5

            pack 6

            pack 9, pack 10, pack 11

        """
        options = {'pack_limit': 0,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 6)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 19)

    def test_group_leftovers(self):
        """ With grouping packs, grouping of leftovers and no limit.

        Given the input packs, we should have dispatches with identical
        content as following:

            pack 1, pack 3, pack 7

            pack 2, pack 8

            pack 9, pack 10, pack 11

            pack 4, pack 5, pack 6 (leftovers)


        """
        options = {'pack_limit': 0,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': True,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 4)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 19)

    def test_group_limit(self):
        """ With grouping packs, no grouping of leftovers and a limit of
        2 without threshold.

        Given the input packs, we should have dispatches with identical
        content as following:

            pack 1, pack 3

            pack 7

            pack 2, pack 8

            pack 4

            pack 5

            pack 6

            pack 9, pack 10

            pack 11

        """
        options = {'pack_limit': 2,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 8)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 19)

    def test_group_leftovers_limit(self):
        """ With grouping packs, grouping of leftovers and limit of 2.

        Given the input packs, we should have dispatches with identical
        content as following:

            pack 1, pack 3,

            pack 2, pack 8

            pack 9, pack 10

            pack 4, pack 5 (leftovers)

            pack 6, pack 7 (leftovers)

            pack 11 (leftovers)

        """
        options = {'pack_limit': 2,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': True,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 6)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 19)

    def test_filter(self):
        """ Without grouping packs, no limit, filter on a group of products.

        Filter on products
             'product.product_product_33'
             'product.product_product_20'

        We should have 4 packs in 1 dispatch.

        """
        pr33 = self.ref('product.product_product_33')
        pr20 = self.ref('product.product_product_20')
        options = {'pack_limit': 0,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [(6, 0, [pr33, pr20])],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 1)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 8)

    def test_filter_group(self):
        """ With grouping packs, no limit, filter on a group of products.

        Filter on products
             'product.product_product_33'
             'product.product_product_20'

        We should have 4 packs in 2 dispatch.

        """
        pr33 = self.ref('product.product_product_33')
        pr20 = self.ref('product.product_product_20')
        options = {'pack_limit': 0,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [(6, 0, [pr33, pr20])],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 2)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 8)

    def test_filter_group_limit(self):
        """ With grouping packs, a limit, filter on a group of products.

        Filter on products
             'product.product_product_33'
             'product.product_product_20'

        With a limit of 2.

        We should have 4 packs in 3 dispatch.

        """
        pr33 = self.ref('product.product_product_33')
        pr20 = self.ref('product.product_product_20')
        options = {'pack_limit': 2,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [(6, 0, [pr33, pr20])],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 3)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 8)

    def test_filter_group_limit_leftovers(self):
        """ With grouping packs and leftovers, a limit, filter on a group of products.

        Filter on products
             'product.product_product_33'
             'product.product_product_20'

        With a limit of 2.

        We should have 4 packs in 2 dispatches (the leftover of first group
        will be grouped with the standalone pack).

        """
        pr33 = self.ref('product.product_product_33')
        pr20 = self.ref('product.product_product_20')
        options = {'pack_limit': 2,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [(6, 0, [pr33, pr20])],
                   'group_by_content': True,
                   'group_leftovers': True,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 2)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 8)

    def test_limit_threshold(self):
        """ Without grouping packs but with a limit and a limit threshold.

        We set a limit of 3 packs per dispatch, it should generate 4
        dispatches. The threshold should have no effect as the packs are
        not grouped.

        """
        options = {'pack_limit': 3,
                   'pack_limit_apply_threshold': True,
                   'only_product_ids': [],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 4)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 19)

    def test_group_limit_threshold(self):
        """ With grouping packs, no grouping of leftovers and a limit of
        2 with threshold.

        Given the input packs, we should have dispatches with identical
        content as following:

            pack 1, pack 3

            pack 7

            pack 2, pack 8

            pack 4

            pack 5

            pack 6

            pack 9, pack 10, pack 11 (threshold when 1 line)

        """
        options = {'pack_limit': 2,
                   'pack_limit_apply_threshold': True,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 7)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 19)

    def test_group_leftovers_limit_threshold(self):
        """ With grouping packs, grouping of leftovers and limit of 2 with a threshold.

        Given the input packs, we should have dispatches with identical
        content as following:

            pack 1, pack 3,

            pack 2, pack 8

            pack 9, pack 10, pack 11 (threshold when 1 line)

            pack 4, pack 5 (leftovers)

            pack 6, pack 7 (leftovers)

        """
        options = {'pack_limit': 2,
                   'pack_limit_apply_threshold': True,
                   'only_product_ids': [],
                   'group_by_content': True,
                   'group_leftovers': True,
                   }
        dispatches = self._call_wizard(options)
        self.assertEquals(len(dispatches), 5)
        moves = [m for dispatch in dispatches for m in dispatch.move_ids]
        self.assertEquals(len(moves), 19)
