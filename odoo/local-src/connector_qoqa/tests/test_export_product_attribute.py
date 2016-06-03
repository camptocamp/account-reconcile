# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import mock

from openerp.addons.connector_qoqa.unit.exporter import export_record
from .common import recorder, QoQaTransactionCase


class TestExportProductAttribute(QoQaTransactionCase):

    def setUp(self):
        super(TestExportProductAttribute, self).setUp()

    def _create_products(self):
        self.product_template = self.env['product.template'].with_context(
            create_product_product=False,
        ).create({
            'name': 'Geelee',
        })
        self.env['product.attribute.line'].create({
            'product_tmpl_id': self.product_template.id,
            'attribute_id': self.color.id,
            'value_ids': [(6, 0, [self.color_red.id, self.color_blue.id])],
        })
        self.env['product.attribute.line'].create({
            'product_tmpl_id': self.product_template.id,
            'attribute_id': self.size.id,
            'value_ids': [(6, 0, [self.size_m.id, self.size_l.id])],
        })

    def _create_attributes(self):
        Attribute = self.env['product.attribute']
        AttributeValue = self.env['product.attribute.value']
        self.color = Attribute.create({
            'name': 'Color',
        })
        self.color_red = AttributeValue.create({
            'attribute_id': self.color.id,
            'name': 'Red',
        })
        self.color_blue = AttributeValue.create({
            'attribute_id': self.color.id,
            'name': 'Blue',
        })
        self.size = Attribute.create({
            'name': 'Size',
        })
        self.size_m = AttributeValue.create({
            'attribute_id': self.size.id,
            'name': 'M',
        })
        self.size_l = AttributeValue.create({
            'attribute_id': self.size.id,
            'name': 'L',
        })

    def test_event_on_binding_create_product_attribute(self):
        """ Export a product attribute when a binding is created """
        self._create_attributes()
        patched = 'openerp.addons.connector_qoqa.consumer.export_record'
        # mock.patch prevents to create the job
        with mock.patch(patched) as export_record_mock:
            binding = self.env['qoqa.product.attribute'].create({
                'backend_id': self.backend_record.id,
                'openerp_id': self.color.id,
            })
            export_record_mock.delay.assert_called_with(
                mock.ANY, 'qoqa.product.attribute', binding.id,
                fields=['backend_id', 'openerp_id']
            )

    def test_event_on_binding_created_product_attribute_value(self):
        """ Export a product attribute when a binding is created """
        self._create_attributes()
        patched = 'openerp.addons.connector_qoqa.consumer.export_record'
        # mock.patch prevents to create the job
        with mock.patch(patched) as export_record_mock:
            binding = self.env['qoqa.product.attribute.value'].create({
                'backend_id': self.backend_record.id,
                'openerp_id': self.color_red.id,
            })
            export_record_mock.delay.assert_called_with(
                mock.ANY, 'qoqa.product.attribute.value', binding.id,
                fields=['backend_id', 'openerp_id']
            )

    def test_export_attribute(self):
        self._create_attributes()
        attribute_no_export = self.env['qoqa.product.attribute'].with_context(
            connector_no_export=True
        )
        binding = attribute_no_export.create({
            'backend_id': self.backend_record.id,
            'openerp_id': self.color.id,
        })
        with recorder.use_cassette('test_export_attribute') as cassette:
            export_record(self.session, 'qoqa.product.attribute', binding.id)
            self.assertEqual(len(cassette.requests), 1)
            response = cassette.responses[0]
            self.assert_cassette_record_exported(response, binding)

    def test_export_attribute_value(self):
        self._create_attributes()
        AttributeValue = self.env['qoqa.product.attribute.value']
        value_no_export = AttributeValue.with_context(
            connector_no_export=True
        )
        binding = value_no_export.create({
            'backend_id': self.backend_record.id,
            'openerp_id': self.color_red.id,
        })
        with recorder.use_cassette('test_export_attribute_value') as cassette:
            export_record(self.session,
                          'qoqa.product.attribute.value',
                          binding.id)
            # one call for the export of the attribute (cascading), one for the
            # value
            self.assertEqual(len(cassette.requests), 2)
            response = cassette.responses[1]
            self.assert_cassette_record_exported(response, binding)

    def test_export_attributes_on_template_export(self):
        """ Check that attributes are exported when a template is exported """
        self._create_attributes()
        self._create_products()
        template_no_export = self.env['qoqa.product.template'].with_context(
            connector_no_export=True
        )
        binding = template_no_export.create({
            'backend_id': self.backend_record.id,
            'openerp_id': self.product_template.id,
        })
        cassette_name = 'test_export_attributes_on_template_export'
        with recorder.use_cassette(cassette_name) as cassette:
            export_record(self.session, 'qoqa.product.template', binding.id)
            # attributes should be exported in cascade
            # 2 requests for attributes color & size and 1 request for the
            # export of the template
            self.assertEqual(len(cassette.requests), 3)
            template_response = cassette.responses[-1]
            self.assert_cassette_record_exported(template_response, binding)

    def test_export_attributes_on_variant_export(self):
        """ Check that attr. values are exported when a variant is exported """
        self._create_attributes()
        self._create_products()
        # generate all the variants!
        self.product_template.create_variant_ids()
        # for the test, we'll export the variant Red-M
        variant = self.product_template.product_variant_ids.filtered(
            lambda rec: (self.color_red in rec.attribute_value_ids and
                         self.size_m in rec.attribute_value_ids)
        )
        product_no_export = self.env['qoqa.product.product'].with_context(
            connector_no_export=True
        )
        binding = product_no_export.create({
            'backend_id': self.backend_record.id,
            'openerp_id': variant.id,
            'default_code': 'Geelee-Red-M',
        })
        cassette_name = 'test_export_attributes_on_variant_export'
        with recorder.use_cassette(cassette_name) as cassette:
            export_record(self.session, 'qoqa.product.product', binding.id)
            # attributes should be exported in cascade
            # we count 6 requests:
            # - 2 requests for attributes color & size
            # - 1 request for the export of the template
            # - 2 requests for the export of the red and M attribute values
            # - 1 request for the export of the product variant
            self.assertEqual(len(cassette.requests), 6)
            variant_response = cassette.responses[-1]
            self.assert_cassette_record_exported(variant_response, binding)
