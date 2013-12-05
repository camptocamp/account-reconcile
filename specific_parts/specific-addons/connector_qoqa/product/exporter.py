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

from openerp.addons.connector.unit.mapper import (mapping,
                                                  none,
                                                  ExportMapper)
from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            )

from ..unit.export_synchronizer import QoQaExporter, Translations

from ..product_attribute.exporter import ProductAttribute
from .. import consumer
from ..backend import qoqa


@on_record_create(model_names='qoqa.product.product')
@on_record_write(model_names='qoqa.product.product')
def delay_export(session, model_name, record_id, fields=None):
    consumer.delay_export(session, model_name, record_id, fields=fields)


@on_record_write(model_names='product.product')
def delay_export_all_bindings(session, model_name, record_id, fields=None):
    if fields == ['qoqa_bind_ids']:
        # QoQa binding edited from the product's view.
        # When only this field has been modified, an other job has
        # been delayed for the qoqa.product.product record.
        return
    consumer.delay_export_all_bindings(session, model_name,
                                       record_id, fields=fields)


@qoqa
class ProductExporter(QoQaExporter):
    _model_name = ['qoqa.product.product']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        assert self.binding_record
        self._export_dependency(self.binding_record.product_tmpl_id,
                                'qoqa.product.template')


@qoqa
class ProductExportMapper(ExportMapper):
    _model_name = 'qoqa.product.product'

    direct = [('default_code', 'sku'),
              (none('ean13'), 'ean'),
              ]

    translatable_fields = [
        ('variants', 'name')
    ]

    @mapping
    def warranty(self, record):
        return {'warranty': record.product_tmpl_id.warranty}

    @mapping
    def todo(self, record):
        # TODO: code is mandatory but I don't know
        # what it should contain
        values = {
            'code': 2,
        }
        return values

    @mapping
    def product_id(self, record):
        binder = self.get_binder_for_model('qoqa.product.template')
        openerp_id = record.product_tmpl_id.id
        qoqa_id = binder.to_backend(openerp_id, wrap=True)
        return {'product_id': qoqa_id}

    @mapping
    def attributes(self, record):
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
