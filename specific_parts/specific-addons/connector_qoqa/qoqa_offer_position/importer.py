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
                                                  changed_by,
                                                  only_create,
                                                  backend_to_m2o,
                                                  ImportMapper)
from openerp.addons.connector.exception import MappingError
from ..backend import qoqa
from ..unit.import_synchronizer import QoQaImportSynchronizer
from ..unit.mapper import ifmissing, iso8601_to_utc, qoqafloat


@qoqa
class QoQaOfferPositionImport(QoQaImportSynchronizer):
    _model_name = 'qoqa.offer.position'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        self._import_dependency(rec['deal_id'], 'qoqa.offer')
        self._import_dependency(rec['product_id'], 'qoqa.product.template')
        self._import_dependency(rec['buyphrase_id'], 'qoqa.buyphrase')
        for var in rec['offer_variations']:
            self._import_dependency(var['variation_id'],
                                    'qoqa.product.product')


@qoqa
class QoQaOfferPositionImportMapper(ImportMapper):
    _model_name = 'qoqa.offer.position'

    # TODO:
    # poste_cumbersome_package
    # is_net_price
    # is_active

    children = [('offer_variations', 'variant_ids',
                 'qoqa.offer.position.variant'),
                ]

    direct = [(backend_to_m2o('deal_id'), 'offer_id'),
              (backend_to_m2o('product_id', binding='qoqa.product.template'),
               'product_tmpl_id'),
              (backend_to_m2o('vat_id'), 'tax_id'),
              (backend_to_m2o('buyphrase_id'), 'buyphrase_id'),
              ('lot_size', 'lot_size'),
              ('max_sellable', 'max_sellable'),
              ('stock_bias', 'stock_bias'),
              (qoqafloat('unit_price'), 'unit_price'),
              (qoqafloat('installment_price'), 'installment_price'),
              (qoqafloat('regular_price'), 'regular_price'),
              (qoqafloat('buy_price'), 'buy_price'),
              (qoqafloat('top_price'), 'top_price'),
              ('ecotax', 'ecotax'),
              (iso8601_to_utc('delivery_at'), 'date_delivery'),
              ('booking_delivery', 'booking_delivery'),
              ('order_url', 'order_url'),
              ]

    @mapping
    def regular_price_type(self, record):
        binder = self.get_binder_for_model('qoqa.regular.price.type')
        binding_id = binder.to_openerp(record['regular_price_type'])
        return {'regular_price_type': binding_id}
