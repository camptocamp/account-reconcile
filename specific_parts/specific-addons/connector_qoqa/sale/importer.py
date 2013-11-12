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
                                                  backend_to_m2o,
                                                  ImportMapper,
                                                  )
from openerp.addons.connector_ecommerce.unit.sale_order_onchange import (
    SaleOrderOnChange)
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        )
from ..unit.mapper import iso8601_to_utc

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
        self._import_dependency(rec['deal_id'], 'qoqa.offer')
        self._import_dependency(rec['user_id'], 'qoqa.res.partner', always=True)
        self._import_dependency(rec['billing_address_id'],
                                'qoqa.address', always=True)
        self._import_dependency(rec['shipping_address_id'],
                                'qoqa.address', always=True)
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

    def _after_import(self, binding_id):
        """ Import lines of sales order """


@qoqa
class SaleOrderImportMapper(ImportMapper):
    _model_name = 'qoqa.sale.order'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              (backend_to_m2o('shop_id'), 'qoqa_shop_id'),
              (backend_to_m2o('shop_id', binding='qoqa.shop'), 'shop_id'),
              (backend_to_m2o('user_id', binding='qoqa.res.partner'), 'partner_id'),
              (backend_to_m2o('shipping_address_id',
                              binding='qoqa.address'),
               'partner_shipping_id'),
              (backend_to_m2o('billing_address_id',
                              binding='qoqa.address'),
               'partner_invoice_id'),
              ]

    @mapping
    def from_offer(self, record):
        """ Get the linked offer and takes some values from there """
        binder = self.get_binder_for_model('qoqa.offer')
        offer_id = binder.to_openerp(record['deal_id'], unwrap=True)
        offer = self.session.browse('qoqa.offer', offer_id)
        return {'offer_id': offer.id, 'pricelist_id': offer.pricelist_id.id}

    def finalize(self, map_record, values):
        sess = self.session
        values['qoqa_order_line_ids'] = self.lines(map_record)
        onchange = self.get_connector_unit_for_model(SaleOrderOnChange)
        return onchange.play(values, values['qoqa_order_line_ids'])

    def lines(self, map_record):
        """ Lines are composed of 2 list of dicts

        1 list is 'order_items', the other is 'items'.
        We keep the id of the 'item' and discard the one of the
        'order_items'.

        """
        lines = []
        for item in map_record.source['items']:
            nitem = item.copy()
            item_id = nitem['id']
            for order_item in map_record.source['order_items']:
                if order_item['item_id'] != item_id:
                    continue
                nitem.update(order_item)
            nitem.pop('id')  # remove id just to avoid confusion
            lines.append(nitem)

        map_child = self.get_connector_unit_for_model(
            self._map_child_class, 'qoqa.sale.order.line')
        items = map_child.get_items(lines, map_record, 'qoqa_order_line_ids',
                                    options=self.options)
        return items


@qoqa
class QoQaSaleOrderOnChange(SaleOrderOnChange):
    _model_name = 'qoqa.sale.order'
