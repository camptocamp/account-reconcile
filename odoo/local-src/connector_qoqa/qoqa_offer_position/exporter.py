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

from datetime import datetime
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ExportMapper,
                                                  )
from openerp.addons.connector.event import (on_record_create,
                                            on_record_write,
                                            )
from ..backend import qoqa
from .. import consumer
from ..unit.export_synchronizer import QoQaExporter, Translations
from ..unit.mapper import (m2o_to_backend,
                           floatqoqa,
                           date_to_iso8601,
                           )


@on_record_create(model_names='qoqa.offer.position')
@on_record_write(model_names='qoqa.offer.position')
def delay_export(session, model_name, record_id, vals):
    # High priority, update of offers should be done as soon as
    # possible.  Priority still lower than offers though, so they have a
    # change to be exported before. Also, set an ETA to now, so others
    # jobs with an ETA won't be executed before (sorting of jobs is:
    # eta, priority, create_date)
    consumer.delay_export(session, model_name, record_id, vals, priority=5,
                          eta=datetime.now())


@qoqa
class OfferPositionExporter(QoQaExporter):
    _model_name = ['qoqa.offer.position']

    def _export_dependencies(self):
        """ Export the dependencies for the record"""
        assert self.binding_record
        binding = self.binding_record
        self._export_dependency(binding.offer_id, 'qoqa.offer')
        self._export_dependency(binding.product_tmpl_id,
                                'qoqa.product.template')
        self._export_dependency(binding.buyphrase_id, 'qoqa.buyphrase')
        for variant in binding.variant_ids:
            self._export_dependency(variant.product_id, 'qoqa.product.product')


@qoqa
class OfferPositionExportMapper(ExportMapper):
    _model_name = 'qoqa.offer.position'

    children = [('variant_ids', 'offer_variations',
                 'qoqa.offer.position.variant'),
                ]

    translatable_fields = []

    only_create_translatable_fields = [
        # fields are edited on QoQa backend and are readonly
        # on OpenERP but we export them on creation so when duplicated
        # the original value is sent to the QoQa backend
        ('description', 'description'),
        ('highlights', 'highlights'),
    ]

    direct = [(floatqoqa('lot_price'), 'unit_price'),
              (floatqoqa('installment_price'), 'installment_price'),
              (floatqoqa('regular_price'), 'regular_price'),
              (floatqoqa('buy_price'), 'buy_price'),
              (floatqoqa('top_price'), 'top_price'),
              (date_to_iso8601('date_delivery'), 'delivery_at'),
              ('booking_delivery', 'booking_delivery'),
              ('order_url', 'order_url'),
              ('stock_bias', 'stock_bias'),
              ('max_sellable', 'max_sellable'),
              ('lot_size', 'lot_size'),
              (m2o_to_backend('buyphrase_id'), 'buyphrase_id'),
              (m2o_to_backend('product_tmpl_id',
                              binding='qoqa.product.template'),
               'product_id'),
              (m2o_to_backend('tax_id'), 'vat_id'),
              (m2o_to_backend('offer_id'), 'deal_id'),
              ('active', 'is_active'),
              ('poste_cumbersome_package', 'poste_cumbersome_package'),
              ]

    @mapping
    def regular_price_type(self, record):
        binder = self.get_binder_for_model('qoqa.regular.price.type')
        binding_id = binder.to_backend(record.regular_price_type)
        return {'regular_price_type': binding_id}

    @mapping
    def currency(self, record):
        currency = record.offer_id.pricelist_id.currency_id
        binder = self.get_binder_for_model('res.currency')
        qoqa_ccy_id = binder.to_backend(currency.id, wrap=True)
        return {'currency_id': qoqa_ccy_id}

    @mapping
    def translations(self, record):
        """ Map all the translatable values

        Translatable fields for QoQa are sent in a `translations`
        key and are not sent in the main record.
        """
        fields = self.translatable_fields[:]
        if self.options.for_create:
            fields += self.only_create_translatable_fields
        trans = self.get_connector_unit_for_model(Translations)
        langs = [record.offer_id.lang_id] if record.offer_id.lang_id else None
        return trans.get_translations(record, normal_fields=fields,
                                      only_langs=langs)
