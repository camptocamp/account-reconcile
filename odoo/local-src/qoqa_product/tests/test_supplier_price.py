# -*- coding: utf-8 -*-
# © 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.tests.common import TransactionCase
from openerp.exceptions import UserError


class TestSupplierPrice(TransactionCase):

    def setUp(self):
        super(TestSupplierPrice, self).setUp()
        self.template = self.env.ref('qoqa_product.template_0')
        self.variant1 = self.env.ref('qoqa_product.variant_1')
        self.variant2 = self.env.ref('qoqa_product.variant_2')
        self.variant3 = self.env.ref('qoqa_product.variant_3')
        self.supplierinfo1 = self.env.ref('qoqa_product.supplierinfo_1')
        self.supplierinfo2 = self.env.ref('qoqa_product.supplierinfo_2')

    def test_variant_prices(self):
        # variant1 has a dedicated supplier (supplierinfo1)
        self.assertEqual(self.variant1.seller_price,
                         self.supplierinfo1.price)
        # variant2 has no dedicated supplier
        # => use template supplier (supplierinfo2)
        self.assertEqual(self.variant2.seller_price,
                         self.supplierinfo2.price)

    def test_updating_variant_price_with_supplierinfo(self):
        """ If a variant has its own supplierinfo, the supplierinfo price is
            updated as well when changing the variant price
        """
        self.variant1.seller_price = 800
        self.assertEqual(self.supplierinfo1.price, 800)

    def test_updating_variant_price_with_no_supplierinfo(self):
        """ If a variant has no related supplierinfo, updating its seller price
            creates a new supplierinfo using the product template supplierinfo
            as default and the variant price.
        """
        # Initially no supplierinfo is related to the variant:
        nb_supplierinfo = self.env['product.supplierinfo'].search_count([
            ('product_id', '=', self.variant2.id)
        ])
        self.assertEqual(nb_supplierinfo, 0)

        # Updating the variant price
        self.variant2.seller_price = 800

        # The product template supplierinfo remains unchanged:
        self.assertEqual(self.supplierinfo2.price, 790)

        # A new supplierinfo has been created and linked to the variant:
        supplierinfo = self.env['product.supplierinfo'].search([
            ('product_id', '=', self.variant2.id)
        ])
        self.assertEqual(len(supplierinfo), 1)
        self.assertEqual(supplierinfo.price, 800)
        self.assertEqual(supplierinfo.name, self.supplierinfo2.name)

    def test_updating_variant_price_with_several_supplierinfo(self):
        """ Check an error is raised if it is not possible to figure the
            supplierinfo out because there are too many.
        """
        with self.assertRaises(UserError):
            self.variant3.seller_price = 1000
