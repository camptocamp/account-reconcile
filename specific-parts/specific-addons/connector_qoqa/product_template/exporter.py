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
                                            )
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper)

from ..product_attribute.exporter import ProductAttribute
from ..product.exporter import (
    delay_export_all_bindings as product_delay_export
)
from ..unit.export_synchronizer import QoQaExporter, Translations
from .. import consumer
from ..backend import qoqa


@on_record_create(model_names='qoqa.product.template')
@on_record_write(model_names='qoqa.product.template')
def delay_export(session, model_name, record_id, vals):
    consumer.delay_export(session, model_name, record_id, vals)


@on_record_write(model_names='product.template')
def delay_export_all_bindings(session, model_name, record_id, vals):
    if 'warranty' in vals:
        # the warranty should be exported on the variant, not the
        # template
        for product in session.browse(model_name, record_id).variant_ids:
            product_delay_export(session, 'product.product',
                                 product.id, {'warranty': vals['warranty']})
        if vals.keys() == ['warranty']:
            # nothing to export on the template
            return
    consumer.delay_export_all_bindings(session, model_name,
                                       record_id, vals)


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
    ]

    @mapping
    def metas(self, record):
        """ QoQa tries to loop on this field

        So it is there only to avoid errors on QoQa.
        But we don't have any values to send.

        """
        return {'product_metas': []}

    @mapping
    def category(self, record):
        if not record.categ_id:
            return
        session = self.session
        qoqa_value = session.pool['product.category'].name_get(
            session.cr, session.uid, record.categ_id.id,
            context={'lang': 'fr_FR'})
        if len(qoqa_value) > 0:
            # Result is [(id, value)]
            return {'category': qoqa_value[0][1]}
        else:
            return

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
        fields = self.translatable_fields  # not including attributes
        trans = self.get_connector_unit_for_model(Translations)
        return trans.get_translations(record, normal_fields=fields,
                                      attributes_unit=ProductAttribute)
