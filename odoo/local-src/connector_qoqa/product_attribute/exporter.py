# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            )
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper)
from ..backend import qoqa
from ..unit.exporter import QoQaExporter, Translations
from .. import consumer

# TODO: export wine values?


@on_record_create(model_names='qoqa.product.attribute')
@on_record_write(model_names='qoqa.product.attribute')
def delay_export(session, model_name, record_id, vals):
    consumer.delay_export(session, model_name, record_id, vals)


@on_record_write(model_names='product.attribute')
def delay_export_all_bindings(session, model_name, record_id, vals):
    consumer.delay_export_all_bindings(session, model_name,
                                       record_id, vals)


@qoqa
class ProductAttributeExporter(QoQaExporter):
    _model_name = ['qoqa.product.attribute']


@qoqa
class ProductAttributeExportMapper(ExportMapper):
    _model_name = 'qoqa.product.attribute'

    translatable_fields = [
        ('name', 'name'),
        # we have no 'description field
        # ('description', 'description'),
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
