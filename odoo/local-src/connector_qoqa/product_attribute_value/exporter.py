# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            )
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper,
                                                  m2o_to_backend)
from ..backend import qoqa
from ..unit.exporter import QoQaExporter, Translations
from .. import consumer


@on_record_create(model_names='qoqa.product.attribute.value')
@on_record_write(model_names='qoqa.product.attribute.value')
def delay_export(session, model_name, record_id, vals):
    consumer.delay_export(session, model_name, record_id, vals)


@on_record_write(model_names='product.attribute.value')
def delay_export_all_bindings(session, model_name, record_id, vals):
    consumer.delay_export_all_bindings(session, model_name,
                                       record_id, vals)


@qoqa
class ProductAttributeValueExporter(QoQaExporter):
    _model_name = ['qoqa.product.attribute.value']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        assert self.binding_record
        self._export_dependency(self.binding_record.attribute_id,
                                'qoqa.product.attribute')


@qoqa
class ProductAttributeValueExportMapper(ExportMapper):
    _model_name = 'qoqa.product.attribute.value'

    direct = [
        (m2o_to_backend('attribute_id', binding='qoqa.product.attribute'),
         'product_attribute_category_id'),
        ('sequence', 'position'),
    ]

    translatable_fields = [
        ('name', 'name'),
    ]

    @mapping
    def translations(self, record):
        """ Map all the translatable values, including the attributes

        Translatable fields for QoQa are sent in a ``translations_attributes``
        key and are not sent in the main record.
        """
        trans = self.unit_for(Translations)
        return trans.get_translations(record,
                                      normal_fields=self.translatable_fields)
