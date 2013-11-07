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

from openerp.addons.connector.unit.mapper import (backend_to_m2o,
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        )

_logger = logging.getLogger(__name__)


@qoqa
class SaleOrderBatchImport(DelayedBatchImport):
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
                                'qoqa.address')
        self._import_dependency(rec['shipping_address_id'],
                                'qoqa.address')
        self._import_dependency(rec['shipping_address_id'],
                                'qoqa.address')
        for item in rec['items']:
            self._import_dependency(item['variation_id'],
                                    'qoqa.product.product')
            self._import_dependency(item['offer_id'],
                                    'qoqa.offer.position')
            # TODO promo_id
            # self._import_dependency(item['promo_id'],
            #                         'qoqa.promo')
        for payment in rec['payments']:
            pass
            # TODO
            # self._import_dependency(item['voucher_id'],
            #                         'qoqa.voucher')


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
                              binding='qoqa.address'),
               'partner_shipping_id'),
              (backend_to_m2o('billing_address_id',
                              binding='qoqa.address'),
               'partner_invoice_id'),
              ]
