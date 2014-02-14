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

Test that the wizard run several times on the same packs
won't put them again in a dispatch

"""

import openerp.tests.common as common
from .common import prepare_move, prepare_pack, create_pack


class test_run_several(common.TransactionCase):

    def setUp(self):
        super(test_run_several, self).setUp()
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

    def _call_wizard(self, pack_ids, options):
        Wizard = self.registry('picking.dispatch.grouper')
        Dispatch = self.registry('picking.dispatch')
        wizard_id = Wizard.create(self.cr, self.uid, options)
        wizard = Wizard.browse(self.cr, self.uid, wizard_id)
        dispatch_ids = Wizard._group_packs(self.cr, self.uid, wizard,
                                           pack_ids)
        if dispatch_ids:
            return Dispatch.browse(self.cr, self.uid, dispatch_ids)

    def test_no_dispatch_again(self):
        """ Do not create a dispatch for packs already in a dispatch.  """
        options = {'pack_limit': 0,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard([self.pack_id_1, self.pack_id_2],
                                       options)
        self.assertEquals(len(dispatches), 1)
        dispatches = self._call_wizard([self.pack_id_1, self.pack_id_2],
                                       options)
        self.assertFalse(dispatches)

    def test_dispatch_remaining(self):
        """ Create a dispatch for the remaining packs when some are already dispatched"""
        options = {'pack_limit': 0,
                   'pack_limit_apply_threshold': False,
                   'only_product_ids': [],
                   'group_by_content': False,
                   'group_leftovers': False,
                   }
        dispatches = self._call_wizard([self.pack_id_1],
                                       options)
        self.assertEquals(len(dispatches), 1)
        self.assertEquals(dispatches[0].move_ids[0].tracking_id.id,
                          self.pack_id_1)
        dispatches = self._call_wizard([self.pack_id_1, self.pack_id_2],
                                       options)
        self.assertEquals(len(dispatches), 1)
        self.assertEquals(dispatches[0].move_ids[0].tracking_id.id,
                          self.pack_id_2)
