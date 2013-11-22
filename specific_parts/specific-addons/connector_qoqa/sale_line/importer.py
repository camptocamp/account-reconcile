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
                                                  ImportMapChild,
                                                  )
from ..backend import qoqa
from ..unit.mapper import iso8601_to_utc

_logger = logging.getLogger(__name__)


QOQA_STATUS_PENDING = 1
QOQA_STATUS_DONE = 2
QOQA_STATUS_CANCELLED = 3

QOQA_TYPE_SOLD = 1
QOQA_TYPE_PURCHASED = 2
QOQA_TYPE_RETURNED = 3


@qoqa
class SaleOrderLineImportMapper(ImportMapper):
    """ Convert 'order_items' and 'items' into sales order lines.

    The 2 dicts are merged, then passed to this Mapper.

    The qoqa ID kept in the binding is the "id" of "items", renamed
    to ``item_id``
    """
    _model_name = 'qoqa.sale.order.line'

    # TODO
    # promo_id
    # lot_size
    # custom_text

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ('quantity', 'qoqa_quantity'),
              ('custom_text', 'custom_text'),
              ('lot_size', 'qoqa_lot_size'),
              ('item_id', 'qoqa_id'),
              (backend_to_m2o('variation_id', binding='qoqa.product.product'),
               'product_id'),
              ]

    @mapping
    def price(self, record):
        q_position_id = record['offer_id']
        binder = self.get_binder_for_model('qoqa.offer.position')
        position_id = binder.to_openerp(q_position_id)
        position = self.session.browse('qoqa.offer.position', position_id)
        return {'price_unit': position.unit_price,
                'offer_position_id': position_id}

    @mapping
    def quantity(self, record):
        """ Quantity is multiplied by the lot size:

        Example: a customer buy 2 x 6 bottles of wine: 12 units

        """
        quantity = record['quantity']
        lot_size = record['lot_size']
        total = quantity * lot_size
        return {'product_uos_qty': total, 'product_uom_qty': total}


@qoqa
class LineMapChild(ImportMapChild):
    _model_name = 'qoqa.sale.order.line'

    def skip_item(self, map_record):
        record = map_record.source
        if record['status_id'] == QOQA_STATUS_CANCELLED:
            return True
        if record['type_id'] != QOQA_TYPE_SOLD:
            return True

    def get_item_values(self, map_record, to_attr, options):
        values = map_record.values(**options)
        binder = self.get_binder_for_model()
        binding_id = binder.to_openerp(map_record.source['item_id'])
        if binding_id is not None:
            # already exists, keeps the id
            values['id'] = binding_id
        return values

    def format_items(self, items_values):
        # if we already have an ID (found in get_item_values())
        # we change the command to update the existing record
        items = []
        for item in items_values[:]:
            if item.get('id'):
                binding_id = item.pop('id')
                # update the record
                items.append((1, binding_id, item))
            else:
                # create the record
                items.append((0, 0, item))
        return items
