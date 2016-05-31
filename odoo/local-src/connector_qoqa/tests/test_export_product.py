# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import mock

from openerp.addons.connector_qoqa.unit.exporter import export_record
from .common import recorder, QoQaTransactionCase


class TestExportProduct(QoQaTransactionCase):

    def setUp(self):
        super(TestExportProduct, self).setUp()
        self._create_products()

    def _create_products(self):
        self.product_template = self.env['product.template'].with_context(
            create_product_product=False,
        ).create({
            'name': 'MRSAFE',
        })
        self.product_variant = self.env['product.product'].create({
            'product_tmpl_id': self.product_template.id,
            'default_code': 'MRSAFE-variant',
        })

    def test_event_on_create_product_template(self):
        """ Export a product template when a binding is created """
        patched = 'openerp.addons.connector_qoqa.consumer.export_record'
        # mock.patch prevents to create the job
        with mock.patch(patched) as export_record_mock:
            self.assertEqual(
                0, self.env['qoqa.product.product'].search_count([])
            )

            binding = self.env['qoqa.product.template'].create({
                'backend_id': self.backend_record.id,
                'openerp_id': self.product_template.id,
            })

            binding_product = self.env['qoqa.product.product'].search([])
            self.assertEqual(1, len(binding_product))
            self.assertEqual(
                self.product_variant, binding_product.openerp_id
            )
            self.assertEqual(
                self.product_template, binding_product.product_tmpl_id
            )

            export_record_mock.delay.assert_has_calls([
                mock.call(
                    mock.ANY, 'qoqa.product.template', binding.id,
                    fields=['backend_id', 'openerp_id']
                ),
                mock.call(
                    mock.ANY, 'qoqa.product.product', binding_product.id,
                    fields=['backend_id', 'openerp_id'], priority=12
                ),
            ])
            ])

    def test_export_product_template(self):
        template_no_export = self.env['qoqa.product.template'].with_context(
            connector_no_export=True
        )
        binding = template_no_export.create({
            'backend_id': self.backend_record.id,
            'openerp_id': self.product_template.id,
        })
        with recorder.use_cassette('test_export_product_template') as cassette:
            export_record(self.session, 'qoqa.product.template', binding.id)
            self.assertEqual(len(cassette.requests), 1)
            response = cassette.responses[0]
            self.assert_cassette_record_exported(response, binding)

    def test_export_product_product(self):
        product_no_export = self.env['qoqa.product.product'].with_context(
            connector_no_export=True
        )
        binding = product_no_export.create({
            'backend_id': self.backend_record.id,
            'openerp_id': self.product_variant.id,
        })
        with recorder.use_cassette('test_export_product_product') as cassette:
            export_record(self.session, 'qoqa.product.product', binding.id)
            # 1 request for template creation, 1 for variant creation
            self.assertEqual(len(cassette.requests), 2)
            response = cassette.responses[1]
            self.assert_cassette_record_exported(response, binding)
