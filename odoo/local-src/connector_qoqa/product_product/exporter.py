# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.addons.connector.unit.mapper import (
    convert, mapping, ExportMapper,
)
from openerp.addons.connector.event import (
    on_record_create, on_record_write,
)

from ..unit.exporter import QoQaExporter

from .. import consumer
from ..backend import qoqa


@on_record_create(model_names='qoqa.product.product')
@on_record_write(model_names='qoqa.product.product')
def delay_export(session, model_name, record_id, vals):
    consumer.delay_export(session, model_name, record_id, vals, priority=12)


@on_record_write(model_names='product.product')
def delay_export_all_bindings(session, model_name, record_id, vals):
    if vals.keys() == ['qoqa_bind_ids']:
        # QoQa binding edited from the product's view.
        # When only this field has been modified, an other job has
        # been delayed for the qoqa.product.product record.
        return
    consumer.delay_export_all_bindings(session, model_name, record_id, vals)


@qoqa
class ProductExporter(QoQaExporter):
    _model_name = ['qoqa.product.product']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        assert self.binding_record
        self._export_dependency(self.binding_record.product_tmpl_id,
                                'qoqa.product.template')
        for attr_value in self.binding_record.attribute_value_ids:
            self._export_dependency(attr_value.attribute_id,
                                    'qoqa.product.attribute')
            self._export_dependency(attr_value, 'qoqa.product.attribute.value')


@qoqa
class ProductExportMapper(ExportMapper):
    _model_name = 'qoqa.product.product'

    direct = [
        ('default_code', 'sku'),
        (convert('warranty', int), 'months_warranty'),
    ]

    def _get_template_qoqa_id(self, record):
        binder = self.binder_for('qoqa.product.template')
        qoqa_id = binder.to_backend(record.product_tmpl_id, wrap=True)
        assert qoqa_id, 'product template should have been exported'
        return qoqa_id

    @mapping
    def template(self, record):
        return {'product_id': self._get_template_qoqa_id(record)}

    @mapping
    def ean(self, record):
        return {'ean': record.barcode or None}

    @mapping
    def wine_bottle(self, record):
        result = {}

        volume = record.wine_bottle_id.volume
        if volume:
            result['liters_capacity'] = volume

        return result

    @mapping
    def attribute_values(self, record):
        attribute_binder = self.binder_for('qoqa.product.attribute')
        value_binder = self.binder_for('qoqa.product.attribute.value')
        attributes = []
        template_qoqa_id = self._get_template_qoqa_id(record)
        for attribute_value in record.attribute_value_ids:
            attribute = attribute_value.attribute_id
            attr_qoqa_id = attribute_binder.to_backend(attribute, wrap=True)
            assert attr_qoqa_id, 'attribute should have been exported'
            value_qoqa_id = value_binder.to_backend(attribute_value, wrap=True)
            assert value_qoqa_id, 'attribute should have been exported'
            attributes.append({
                'product_attribute_id': value_qoqa_id,
                'position': attribute_value.sequence,
                'product_category_attributes': {
                    'product_attribute_category_id': attr_qoqa_id,
                    'position': attribute.sequence,
                    'product_id': template_qoqa_id,
                }
            })

        return {'product_attribute_variations_attributes': attributes}
