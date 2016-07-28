# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import BatchGroupTestCase


class TestLeftovers(BatchGroupTestCase):

    @classmethod
    def setUpClass(cls):
        """
        Setup the moves before creating the dispatches.

        packs 1 and 3 are identical (same content)

        packs 2 and 4 and 6 are different but have the same quantity (3)

        packs 5 and 7 are different but have the same quantity (2)

        packs 8,9,10,11,12 all have 1 unit (all different)

        """
        BatchGroupTestCase.setUpClass()
        cls.pack_1 = cls.create_pack([
            (cls.p1, 1),
            (cls.p2, 1),
        ])

        cls.pack_2 = cls.create_pack([
            (cls.p3, 1),
            (cls.p2, 1),
            (cls.p9, 1),
        ])

        cls.pack_3 = cls.create_pack([
            (cls.p1, 1),
            (cls.p2, 1),
        ])

        cls.pack_4 = cls.create_pack([
            (cls.p1, 2),
            (cls.p2, 1),
        ])

        cls.pack_5 = cls.create_pack([
            (cls.p4, 2),
        ])

        cls.pack_6 = cls.create_pack([
            (cls.p1, 2),
            (cls.p5, 1),
        ])

        cls.pack_7 = cls.create_pack([
            (cls.p5, 2),
        ])

        cls.pack_8 = cls.create_pack([
            (cls.p6, 1),
        ])

        cls.pack_9 = cls.create_pack([
            (cls.p7, 1),
        ])

        cls.pack_10 = cls.create_pack([
            (cls.p8, 1),
        ])

        cls.pack_11 = cls.create_pack([
            (cls.p9, 1),
        ])

        cls.pack_12 = cls.create_pack([
            (cls.p3, 1),
        ])

        for num in range(1, 13):
            cls.all_packs |= getattr(cls, 'pack_%d' % num)

    def test_leftovers(self):
        """ Test leftovers and leftovers of leftovers

        Given the input packs, we should have dispatches with identical
        content as following:

            packs 1, 3 (group)

            packs 2, 4, 6 (leftover grouped by qty of 3)

            packs 5, 7 (leftover grouped by qty of 2)

            packs 8, 9, 10, 11, 12 (leftover grouped by qty of 1)

        """
        options = {
            'pack_limit': 0,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [],
            'group_by_content': True,
            'group_leftovers': True,
        }
        batches = self._call_wizard(options)
        self.assertEquals(4, len(batches))

        self.check_packs(batches, [
            (self.pack_1, self.pack_3),
            (self.pack_2, self.pack_4, self.pack_6),
            (self.pack_5, self.pack_7),
            (self.pack_8, self.pack_9, self.pack_10, self.pack_11,
             self.pack_12),
        ])

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
        options = {
            'pack_limit': 2,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [],
            'group_by_content': True,
            'group_leftovers': True,
        }
        batches = self._call_wizard(options)
        self.assertEquals(6, len(batches))

        self.check_packs(batches, [
            (self.pack_1, self.pack_3),
            (self.pack_2, self.pack_4),
            (self.pack_5, self.pack_7),
            (self.pack_8, self.pack_9),
            (self.pack_10, self.pack_11),
            (self.pack_6, self.pack_12),
        ]),
