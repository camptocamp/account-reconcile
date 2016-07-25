# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

"""

Test that the wizard run several times on the same packs
won't put them again in a dispatch

"""
from openerp.exceptions import UserError
from .common import BatchGroupTestCase


class TestRunSeveral(BatchGroupTestCase):

    @classmethod
    def setUpClass(cls):
        BatchGroupTestCase.setUpClass()
        cls.pack_1 = cls.create_pack([
            (cls.p1, 10),
            (cls.p2, 10),
        ])

        cls.pack_2 = cls.create_pack([
            (cls.p3, 5),
            (cls.p2, 10),
        ])
        cls.all_packs |= cls.pack_1 | cls.pack_2

    def test_no_dispatch_again(self):
        """ Do not create a dispatch for packs already in a dispatch.
        """
        options = {
            'pack_limit': 0,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [],
            'group_by_content': False,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(1, len(batches))

        with self.assertRaises(UserError):
            self._call_wizard(options)

    def test_dispatch_remaining(self):
        """ Create a dispatch for the remaining packs after a dispatch
        """
        options = {
            'pack_limit': 0,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [],
            'group_by_content': False,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options, self.pack_1)
        self.assertEquals(1, len(batches))
        self.check_packs(batches, [(self.pack_1,)])

        batches = self._call_wizard(
            options, self.all_packs
        )
        self.assertEquals(1, len(batches))
        self.check_packs(batches, [(self.pack_2,)])
