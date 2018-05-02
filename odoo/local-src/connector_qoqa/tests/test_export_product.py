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
        self.brand = self.env['product.brand'].create({
            'name': 'Things',
        })
        self.category = self.env['product.category'].create({
            'name': 'Test Category',
        })
        self.product_template = self.env['product.template'].with_context(
            create_product_product=False,
        ).create({
            'name': 'MRSAFE',
            'warranty': 12,
            'product_brand_id': self.brand.id,
            'categ_id': self.category.id,
        })

        wine_bottle = self.env['wine.bottle'].create({
            'name': 'Chateauneuf-du-Pape',
            'volume': 0.75,
        })
        self.product_variant = self.env['product.product'].create({
            'product_tmpl_id': self.product_template.id,
            'default_code': 'MRSAFE-variant',
            'wine_bottle_id': wine_bottle.id,
            'barcode': '0190893412216'
        })

    def _check_product_body(self, path, query_json, saved_json):
        """ We check real request datas in addition to compare with cassette.
        """
        if path != '/v1/admin/variations/':
            return super(TestExportProduct, self)._check_json_body(
                path, query_json, saved_json
            )
        else:
            test_product = query_json['variation']
            saved_product = saved_json['variation']

            if sorted(test_product.keys()) != sorted(saved_product.keys()):
                return False

            # serial values can't be compared
            serial_fields = ('product_id',)
            self.assertEqual(
                {k: v for k, v in test_product.items()
                 if k not in serial_fields},
                {k: v for k, v in saved_product.items()
                 if k not in serial_fields}
            )

            # Check real request values.
            template_binding = self.env['qoqa.product.template'].search([
                ('backend_id', '=', self.backend_record.id),
                ('openerp_id', '=', self.product_template.id),
            ])
            self.assertEqual(1, len(template_binding))

            self.assertEqual(
                template_binding.qoqa_id, test_product['product_id']
            )
            self.assertEqual('MRSAFE-variant', test_product['sku'])
            self.assertEqual(0.75, test_product['liters_capacity'])
            self.assertEqual(12, test_product['months_warranty'])
            self.assertEqual('0190893412216', test_product['ean'])

        return True

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

    def test_event_on_update_product_template(self):
        """ Test that product_template update triggers right export.
        """
        patched = 'openerp.addons.connector_qoqa.consumer.export_record'
        # mock.patch prevents to create the job
        with mock.patch(patched) as export_record_mock:
            binding_template = self.env['qoqa.product.template'].create({
                'backend_id': self.backend_record.id,
                'openerp_id': self.product_template.id,
            })
            binding_product = self.env['qoqa.product.product'].search([])

            export_record_mock.reset_mock()

            # update no qoqa variant fields
            self.product_template.write({'description': 'test'})

            export_record_mock.delay.assert_has_calls([
                mock.call(
                    mock.ANY, 'qoqa.product.template', binding_template.id,
                    fields=['description']
                ),
            ])

            export_record_mock.reset_mock()

            # update variant fields push product too
            self.product_template.write(
                {'description': 'test', 'warranty': 14}
            )

            export_record_mock.delay.assert_has_calls([
                mock.call(
                    mock.ANY, 'qoqa.product.product', binding_product.id,
                    fields=['warranty']
                ),
                mock.call(
                    mock.ANY, 'qoqa.product.template', binding_template.id,
                    fields=['description']
                ),
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

        vcr_name = 'test_export_product_product'
        match_on = recorder.match_on + ('json_body',)
        with recorder.use_cassette(vcr_name, match_on=match_on) as cassette:
            export_record(self.session, 'qoqa.product.product', binding.id)
            # 1 request for template creation, 1 for variant creation
            self.assertEqual(len(cassette.requests), 2)
            response = cassette.responses[1]
            self.assert_cassette_record_exported(response, binding)
