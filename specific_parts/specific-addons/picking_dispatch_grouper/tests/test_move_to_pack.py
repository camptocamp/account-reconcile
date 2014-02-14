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

The wizard works on packs but we can use it from moves.
When only a part of the moves of a pack are selected,
the whole pack should be discarded.

"""

import openerp.tests.common as common
from .common import prepare_move, prepare_pack, create_pack, create_move


class test_move_to_pack(common.TransactionCase):

    def setUp(self):
        super(test_move_to_pack, self).setUp()
        self.move_1 = create_move(
            self,
            prepare_move(self, 'product.product_product_33', 10)
        )
        self.move_2 = create_move(
            self,
            prepare_move(self, 'product.product_product_20', 10)
        )
        self.move_3 = create_move(
            self,
            prepare_move(self, 'product.product_product_31', 10)
        )
        self.move_4 = create_move(
            self,
            prepare_move(self, 'product.product_product_31', 5)
        )
        self.move_5 = create_move(
            self,
            prepare_move(self, 'product.product_product_20', 10)
        )

        self.pack_id_1 = create_pack(
            self,
            prepare_pack(self),
            [self.move_1,
             self.move_2,
             self.move_3,
             ])

        self.pack_id_2 = create_pack(
            self,
            prepare_pack(self),
            [self.move_4,
             self.move_5,
             ])

    def test_pack_full(self):
        """ When all moves of a pack are selected, the pack is selected """
        Wizard = self.registry('picking.dispatch.grouper')
        pack_ids = Wizard._move_to_pack_ids(
            self.cr, self.uid,
            [self.move_1, self.move_2,
             self.move_3, self.move_4,
             self.move_5,
             ])

        self.assertEquals(len(pack_ids), 2)

    def test_pack_incomplete(self):
        """ When not all moves of a pack are selected, the pack is discarded """
        Wizard = self.registry('picking.dispatch.grouper')
        pack_ids = Wizard._move_to_pack_ids(
            self.cr, self.uid,
            [self.move_1, self.move_2,
             self.move_4,
             ])
        self.assertEquals(len(pack_ids), 0)

    def test_pack_incomplete_and_full(self):
        """ An incomplete pack does not prevent complete packs to be selected """
        Wizard = self.registry('picking.dispatch.grouper')
        pack_ids = Wizard._move_to_pack_ids(
            self.cr, self.uid,
            [self.move_1, self.move_2,
             self.move_4, self.move_5
             ])
        self.assertEquals(len(pack_ids), 1)
