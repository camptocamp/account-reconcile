# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            )
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper)

from ..unit.exporter import QoQaExporter, Translations
from .. import consumer
from ..backend import qoqa


@on_record_create(model_names='qoqa.product.template')
@on_record_write(model_names='qoqa.product.template')
def delay_export(session, model_name, record_id, vals):
    consumer.delay_export(session, model_name, record_id, vals)


@on_record_write(model_names='product.template')
def delay_export_all_bindings(session, model_name, record_id, vals):
    consumer.delay_export_all_bindings(session, model_name,
                                       record_id, vals)


@qoqa
class TemplateExporter(QoQaExporter):
    _model_name = ['qoqa.product.template']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        assert self.binding_record
        for attr_line in self.binding_record.attribute_line_ids:
            self._export_dependency(
                attr_line.attribute_id,
                'qoqa.product.attribute',
            )


@qoqa
class TemplateExportMapper(ExportMapper):
    """ Example of message:

    ::

        POST /v1/admin/products
        {
          "product": {
            "translations_attributes": [
              {
                "locale": "fr",
                "name": "Product name FR",
                "brand": "Brand test FR"
              },
              {
                "locale": "de",
                "name": "Product name DE",
                "brand": "Brand test DE"
              }
            ]
          }
        }
        200
        {
          "data": {
            "id": 1000005
          }
        }


    """
    _model_name = 'qoqa.product.template'

    translatable_fields = [
        ('name', 'name'),
        # TODO: brand
        ('brand', 'brand'),
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
