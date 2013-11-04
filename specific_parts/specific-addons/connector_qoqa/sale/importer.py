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

import logging

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  backend_to_m2o,
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.import_synchronizer import (FromDateDelayBatchImport,
                                        QoQaImportSynchronizer,
                                        )

_logger = logging.getLogger(__name__)


@qoqa
class SaleOrderBatchImport(FromDateDelayBatchImport):
    """ Import the QoQa Sales Order.

    For every sales order's id in the list, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.sale.order'


@qoqa
class SaleOrderImport(QoQaImportSynchronizer):
    _model_name = 'qoqa.sale.order'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        self._import_dependency(rec['shop_id'], 'qoqa.shop')
        self._import_dependency(rec['deal_id'], 'qoqa.deal')
        self._import_dependency(rec['user_id'], 'qoqa.res.partner')
        self._import_dependency(rec['billing_address_id'],
                                'qoqa.res.partner.address')
        self._import_dependency(rec['shipping_address_id'],
                                'qoqa.res.partner.address')
        self._import_dependency(rec['shipping_address_id'],
                                'qoqa.res.partner.address')
        for item in rec['items']:
            self._import_dependency(item['variation_id'],
                                    'qoqa.product.product')
            self._import_dependency(item['offer_id'],
                                    'qoqa.offer.position')
            # TODO promo_id




@qoqa
class SaleOrderImportMapper(ImportMapper):
    _model_name = 'qoqa.sale.order'

    direct = [('created_at', 'created_at'),
              ('updated_at', 'updated_at'),
              (backend_to_m2o('shop_id'), 'qoqa_shop_id'),
              (backend_to_m2o('shop_id', binding='qoqa.shop_id'), 'shop_id'),
              (backend_to_m2o('deal_id'), 'offer_id'),
              (backend_to_m2o('user_id', binding='qoqa.res.partner'), 'partner_id'),
              (backend_to_m2o('shipping_address_id',
                              binding='qoqa.res.partner.address'),
               'partner_shipping_id'),
              (backend_to_m2o('billing_address_id',
                              binding='qoqa.res.partner.address'),
               'partner_invoice_id'),
              ]



"""

{"id":1010695,
 "shop_id":10,
 "deal_id":5464,
 "user_id":34238,
 "billing_address_id":874724,
 "shipping_address_id":874724,
 "shipper_relay_id":null,
 "type_id":2,
 "status_id":3,
 "shipper_service_id":2,
 "application_origin_id":null,
 "created_at":"2013-10-11T17:34:41+0200",
 "updated_at":"2013-10-11T17:35:03+0200",
 "order_items":[
    {"id":3087350,
     "order_id":1010695,
     "item_id":3568541,
     "type_id":1,
     "status_id":1,
     "quantity":1,
     "delivery_at":"2013-10-28T00:00:00+0100",
     "created_at":"2013-10-11T17:34:42+0200",
     "updated_at":"2013-10-11T17:34:42+0200"}
 ],
 "items":[
   {"id":3568541,
    "type_id":1,
    "offer_id":5447,
    "variation_id":10183,
    "promo_id":17422,
    "stock_id":null,
    "lot_size":1,
    "custom_text":null,
    "created_at":"2013-10-11T17:34:42+0200",
    "updated_at":"2013-10-11T17:34:42+0200"}
 ],
 "payments":[
    {"id":1377427,
     "parent_id":null,
     "type_id":2,
     "user_id":34238,
     "order_id":1010695,
     "invoice_id":898901,
     "currency_id":1,
     "status_id":5,
     "settlement_status_id":2,
     "method_id":1,
     "provider_id":7,
     "voucher_id":null,
     "account":"3000007003",
     "amount":2950,
     "transaction":"131011173501376765",
     "trx_date":"2013-10-11T17:35:03+0200",
     "acq_auth_code":761035,
     "batch":null,
     "book_line_id":null,
     "payout_id":null,
     "created_at":"2013-10-11T17:34:59+0200",
     "updated_at":"2013-10-11T17:35:03+0200"}],
 "order_returns":[]},

"""
