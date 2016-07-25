# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import BatchGroupTestCase


class TestAutomaticGroup(BatchGroupTestCase):

    @classmethod
    def setUpClass(cls):
        BatchGroupTestCase.setUpClass()
        cls.pack_1 = cls.create_pack([
            (cls.p1, 10),
            (cls.p2, 10),
        ])

        cls.pack_2 = cls.create_pack([
            (cls.p3, 5),
            (cls.p2, 10)
        ])

        cls.pack_3 = cls.create_pack([
            (cls.p1, 10),
            (cls.p2, 10),
        ])

        cls.pack_4 = cls.create_pack([
            (cls.p1, 5),
            (cls.p2, 10),
        ])

        cls.pack_5 = cls.create_pack([
            (cls.p1, 5),
            (cls.p2, 10),
            (cls.p4, 1),
        ])

        cls.pack_6 = cls.create_pack([
            (cls.p3, 5),
        ])

        cls.pack_7 = cls.create_pack([
            (cls.p1, 10),
            (cls.p2, 10),
        ])

        cls.pack_8 = cls.create_pack([
            (cls.p2, 10),
            (cls.p3, 5),
        ])

        cls.pack_9 = cls.create_pack([
            (cls.p3, 1),
        ])

        cls.pack_10 = cls.create_pack([
            (cls.p3, 1),
        ])

        cls.pack_11 = cls.create_pack([
            (cls.p3, 1),
        ])

        for num in range(1, 12):
            cls.all_packs |= getattr(cls, 'pack_%d' % num)

    def test_all_off(self):
        """ Without grouping packs and without limit.

        Should generate 1 dispatch.
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
        self.assertEquals(11, len(batches.picking_ids))

    def test_limit(self):
        """ Without grouping packs but with a limit.

        We set a limit of 3 packs per dispatch, it should generate 4
        batches.

        """
        options = {
            'pack_limit': 3,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [],
            'group_by_content': False,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(4, len(batches))

        # Can't know which packs in which batch.
        self.assertItemsEqual(
            [3, 3, 3, 2],
            [len(batch.picking_ids) for batch in batches]
        )

    def test_group(self):
        """ With grouping packs, no grouping of leftovers and no size limit.

        Given the input packs, we should have batches with identical
        content as following:

            pack 1, pack 3, pack 7

            pack 2, pack 8

            pack 4

            pack 5

            pack 6

            pack 9, pack 10, pack 11

        """
        options = {
            'pack_limit': 0,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [],
            'group_by_content': True,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(6, len(batches))
        self.check_packs(batches, [
            (self.pack_1, self.pack_3, self.pack_7),
            (self.pack_2, self.pack_8),
            (self.pack_4,),
            (self.pack_5,),
            (self.pack_6,),
            (self.pack_9, self.pack_10, self.pack_11),
        ])

    def test_group_leftovers(self):
        """ With grouping packs, grouping of leftovers and no limit.

        Given the input packs, we should have batches with identical
        content as following:

            pack 1, pack 3, pack 7

            pack 2, pack 8

            pack 9, pack 10, pack 11

            pack 4, pack 5, pack 6 (leftovers)


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
            (self.pack_1, self.pack_3, self.pack_7),
            (self.pack_2, self.pack_8),
            (self.pack_9, self.pack_10, self.pack_11),
            (self.pack_4, self.pack_5, self.pack_6),
        ])

    def test_group_limit(self):
        """ With grouping packs, no grouping of leftovers and a limit of
        2 without threshold.

        Given the input packs, we should have batches with identical
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
        options = {
            'pack_limit': 2,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [],
            'group_by_content': True,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(8, len(batches))
        self.check_packs(batches, [
            (self.pack_1, self.pack_3),
            (self.pack_7,),
            (self.pack_2, self.pack_8),
            (self.pack_4,),
            (self.pack_5,),
            (self.pack_6,),
            (self.pack_9, self.pack_10),
            (self.pack_11,),
        ])

    def test_group_leftovers_limit(self):
        """ With grouping packs, grouping of leftovers and limit of 2.

        Given the input packs, we should have batches with identical
        content as following:

            pack 1, pack 3,

            pack 2, pack 8

            pack 9, pack 10

            pack 4, pack 5 (leftovers)

            pack 6, pack 11 (leftovers)

            pack 7 (leftovers)

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
            (self.pack_2, self.pack_8),
            (self.pack_9, self.pack_10),
            (self.pack_4, self.pack_5),
            (self.pack_6, self.pack_11),
            (self.pack_7,),
        ])

    def test_filter(self):
        """ Without grouping packs, no limit, filter on a group of products.

        Filter on products
             self.p1
             self.p2

        We should have 4 packs in 1 dispatch.

        """
        options = {
            'pack_limit': 0,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [(6, 0, [self.p1.id, self.p2.id])],
            'group_by_content': False,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(1, len(batches))
        self.check_packs(batches, [
            (self.pack_1, self.pack_3, self.pack_4, self.pack_7)
        ])

    def test_filter_group(self):
        """ With grouping packs, no limit, filter on a group of products.

        Filter on products
             self.p1
             self.p2

        We should have 4 packs in 2 dispatch.

        """
        options = {
            'pack_limit': 0,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [(6, 0, [self.p1.id, self.p2.id])],
            'group_by_content': True,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(2, len(batches))
        self.check_packs(batches, [
            (self.pack_1, self.pack_3, self.pack_7),
            (self.pack_4,)
        ])

    def test_filter_group_limit(self):
        """ With grouping packs, a limit, filter on a group of products.

        Filter on products
             self.p1
             self.p2

        With a limit of 2.

        We should have 4 packs in 3 dispatch.

        """
        options = {
            'pack_limit': 2,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [(6, 0, [self.p1.id, self.p2.id])],
            'group_by_content': True,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(3, len(batches))
        self.check_packs(batches, [
            (self.pack_1, self.pack_3),
            (self.pack_7,),
            (self.pack_4,),
        ])

    def test_filter_group_limit_leftovers(self):
        """ With grouping packs and leftovers, a limit,
        filter on a group of products.

        Filter on products
             self.p1
             self.p2

        With a limit of 2.

        We should have 4 packs in 2 batches (the leftover of first group
        will be grouped with the standalone pack).

        """
        options = {
            'pack_limit': 2,
            'pack_limit_apply_threshold': False,
            'only_product_ids': [(6, 0, [self.p1.id, self.p2.id])],
            'group_by_content': True,
            'group_leftovers': True,
        }
        batches = self._call_wizard(options)
        self.assertEquals(2, len(batches))
        self.check_packs(batches, [
            (self.pack_1, self.pack_3),
            (self.pack_4, self.pack_7,),
        ])

    def test_limit_threshold(self):
        """ Without grouping packs but with a limit and a limit threshold.

        We set a limit of 3 packs per dispatch, it should generate 4
        batches. The threshold should have no effect as the packs are
        not grouped.

        """
        options = {
            'pack_limit': 3,
            'pack_limit_apply_threshold': True,
            'only_product_ids': [],
            'group_by_content': False,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(4, len(batches))

        # Can't know which packs in which batch.
        self.assertItemsEqual(
            [3, 3, 3, 2],
            [len(batch.picking_ids) for batch in batches]
        )

    def test_group_limit_threshold(self):
        """ With grouping packs, no grouping of leftovers and a limit of
        2 with threshold.

        Given the input packs, we should have batches with identical
        content as following:

            pack 1, pack 3

            pack 7

            pack 2, pack 8

            pack 4

            pack 5

            pack 6

            pack 9, pack 10, pack 11 (threshold when 1 line)

        """
        options = {
            'pack_limit': 2,
            'pack_limit_apply_threshold': True,
            'only_product_ids': [],
            'group_by_content': True,
            'group_leftovers': False,
        }
        batches = self._call_wizard(options)
        self.assertEquals(7, len(batches))

        self.check_packs(batches, [
            (self.pack_1, self.pack_3),
            (self.pack_7,),
            (self.pack_2, self.pack_8),
            (self.pack_4,),
            (self.pack_5,),
            (self.pack_6,),
            (self.pack_9, self.pack_10, self.pack_11),
        ])

    def test_group_leftovers_limit_threshold(self):
        """ With grouping packs, grouping of leftovers and limit of 2 with a threshold.

        Given the input packs, we should have batches with identical
        content as following:

            pack 1, pack 3,

            pack 2, pack 8

            pack 9, pack 10, pack 11 (threshold when 1 line)

            pack 4, pack 6 (leftovers)

            pack 5, pack 7 (leftovers)

        Leftovers are sorted by product quantities.
        """
        options = {
            'pack_limit': 2,
            'pack_limit_apply_threshold': True,
            'only_product_ids': [],
            'group_by_content': True,
            'group_leftovers': True,
        }
        batches = self._call_wizard(options)
        self.assertEquals(5, len(batches))

        self.check_packs(batches, [
            (self.pack_1, self.pack_3),
            (self.pack_2, self.pack_8),
            (self.pack_9, self.pack_10, self.pack_11),
            (self.pack_4, self.pack_6),
            (self.pack_5, self.pack_7),
        ])
