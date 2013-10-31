# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            on_record_unlink,
                                            )
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper)

from ..product_attribute.exporter import ProductAttribute
from ..unit.export_synchronizer import QoQaExporter, Translations
from ..unit.delete_synchronizer import QoQaDeleteSynchronizer
from .. import consumer
from ..backend import qoqa


@on_record_create(model_names='qoqa.product.template')
@on_record_write(model_names='qoqa.product.template')
def delay_export(session, model_name, record_id, fields=None):
    consumer.delay_export(session, model_name, record_id, fields=fields)


@on_record_write(model_names='product.template')
def delay_export_all_bindings(session, model_name, record_id, fields=None):
    consumer.delay_export_all_bindings(session, model_name,
                                       record_id, fields=fields)


@on_record_unlink(model_names='qoqa.product.template')
def delay_unlink(session, model_name, record_id):
    consumer.delay_unlink(session, model_name, record_id)


@qoqa
class TemplateDeleteSynchronizer(QoQaDeleteSynchronizer):
    """ Product deleter for QoQa """
    _model_name = ['qoqa.product.template']


@qoqa
class TemplateExporter(QoQaExporter):
    _model_name = ['qoqa.product.template']


@qoqa
class TemplateExportMapper(ExportMapper):
    """ Example of expected JSON to create a template:

        {"product":
            {"translations":
                [{"language_id": 1,
                  "brand": "Brando",
                  "name": "ZZZ",
                  "highlights": "blabl loerm",
                  "description": "lorefjusdhdfujhsdifgh hfduihsi"},
                 {"language_id": 2,
                 "brand": "Brandette",
                 "name": "XXX",
                 "highlights": "el blablo loerm",
                 "description": "d hfduihsi"}
                 ]
            }
        }
    """
    _model_name = 'qoqa.product.template'

    direct = []

    translatable_fields = [
        ('name', 'name'),
        ('description_sale', 'description')
    ]

    @mapping
    def attributes(self, record):
        """ Map attributes which are not translatables """
        attrs = self.get_connector_unit_for_model(ProductAttribute)
        return attrs.get_values(record, translatable=False)

    @mapping
    def translations(self, record):
        """ Map all the translatable values, including the attributes

        Translatable fields for QoQa are sent in a ``translations``
        key and are not sent in the main record.
        """
        # translatable but not attribute
        fields = self.translatable_fields
        trans = self.get_connector_unit_for_model(Translations)
        return trans.get_translations(record, normal_fields=fields,
                                      attributes_unit=ProductAttribute)
