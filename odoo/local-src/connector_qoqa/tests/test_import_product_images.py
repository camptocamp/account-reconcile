# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from .common import recorder, QoQaTransactionCase


class TestImportProductImages(QoQaTransactionCase):
    """ Test the import of product images from QoQa.  """

    def setUp(self):
        super(TestImportProductImages, self).setUp()
        self.QoQaTemplate = self.env['qoqa.product.template']
        self.setup_company()
        self.sync_metadata()
        self._create_products()

    def _create_products(self):
        self.product_template = self.env['product.template'].with_context(
            create_product_product=False,
        ).create({
            'name': 'iPhone 6 / 64GB',
        })
        self.template_binding = self.QoQaTemplate.create({
            'backend_id': self.backend_record.id,
            'openerp_id': self.product_template.id,
            'qoqa_id': '1000001',
        })
        for idx in range(1, 9):
            self.env['qoqa.product.product'].create({
                'product_tmpl_id': self.template_binding.id,
                'backend_id': self.backend_record.id,
                'qoqa_id': str(idx),
                'default_code': 'test-import-image-%d' % idx,
            })

    def test_import_product_images(self):
        with recorder.use_cassette('test_import_product_images'):
            self.template_binding.import_images()
            self.assertTrue(self.template_binding.image)
            for variant in self.template_binding.product_variant_ids:
                self.assertTrue(variant.image)
