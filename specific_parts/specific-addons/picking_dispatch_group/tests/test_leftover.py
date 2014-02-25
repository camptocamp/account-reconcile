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


class test_leftover(common.TransactionCase):

    def setUp(self):
        """
        Setup the moves before creating the dispatches.

        packs 1 and 3 are identical (same content)

        packs 2 and 4 and 6 are different but have the same quantity (3)

        packs 5 and 7 are different but have the same quantity (2)

        packs 8,9,10,11,12 all have 1 unit (all different)

        """
        super(test_leftover, self).setUp()
        self.pack_id_1 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 1),
             prepare_move(self, 'product.product_product_20', 1),
             ])

        self.pack_id_2 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_31', 1),
             prepare_move(self, 'product.product_product_20', 1),
             prepare_move(self, 'product.product_product_21', 1),
             ])

        self.pack_id_3 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 1),
             prepare_move(self, 'product.product_product_20', 1),
             ])

        self.pack_id_4 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 2),
             prepare_move(self, 'product.product_product_20', 1),
             ])

        self.pack_id_5 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_24', 2),
             ])

        self.pack_id_6 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_33', 2),
             prepare_move(self, 'product.product_product_26', 1),
             ])

        self.pack_id_7 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_26', 2),
             ])

        self.pack_id_8 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_32', 1),
             ])

        self.pack_id_9 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_34', 1),
             ])

        self.pack_id_10 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_25', 1),
             ])

        self.pack_id_11 = create_pack(
            self,
            prepare_pack(self),
            [prepare_move(self, 'product.product_product_35', 1),
             ])

        self.pack_id_12 = create_pack(
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
                             self.pack_id_12,
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

    def test_leftovers(self):
        """ Test leftovers and leftovers of leftovers

        Given the input packs, we should have dispatches with identical
        content as following:

            packs 1, 3 (group)

            packs 2, 4, 6 (leftover grouped by qty of 3)

            packs 5, 7 (leftover grouped by qty of 2)

            packs 8, 9, 10, 11, 12 (leftover grouped by qty of 1)

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
        self.assertEquals(len(moves), 18)

    def test_leftovers_limit(self):
        """ Test leftovers and leftovers of leftovers

        Given the input packs, we should have dispatches with identical
        content as following:

            packs 1, 3 (group)

            packs 2, 4 (leftover grouped by qty of 3)

            packs 5, 7 (leftover grouped by qty of 2)

            packs 8, 9 (leftover grouped by qty of 1)

            packs 10, 11 (leftover grouped by qty of 1)

            packs 6, 12 (leftover of leftovers)

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
        self.assertEquals(len(moves), 18)
