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

from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  ImportMapChild,
                                                  )
from openerp.addons.connector_ecommerce.sale import (ShippingLineBuilder,
                                                     SpecialOrderLineBuilder,
                                                     )
from ..backend import qoqa
from ..unit.mapper import iso8601_to_utc, qoqafloat

_logger = logging.getLogger(__name__)

# http://admin.test02.qoqa.com/orderItemStatus
QOQA_STATUS_PENDING = 1
QOQA_STATUS_DONE = 2
QOQA_STATUS_CANCELLED = 3

# http://admin.test02.qoqa.com/orderItemType
QOQA_TYPE_SOLD = 1
QOQA_TYPE_PURCHASED = 2
QOQA_TYPE_RETURNED = 3

# http://admin.test02.qoqa.com/itemType
QOQA_ITEM_PRODUCT = 1
QOQA_ITEM_SHIPPING = 2
QOQA_ITEM_DISCOUNT = 3
QOQA_ITEM_SERVICE = 4

# http://admin.test02.qoqa.com/promoType
QOQA_PROMO_CUSTOMER_SERVICE = 1  # discount
QOQA_PROMO_MARKETING = 2  # marketing
QOQA_PROMO_AFFILIATION = 3  # marketing
QOQA_PROMO_STAFF = 4  # marketing
QOQA_PROMO_MAILING = 5  # ?


@qoqa
class SaleOrderLineImportMapper(ImportMapper):
    """ Convert 'order_items' and 'items' into sales order lines.

    The 2 dicts are merged, then passed to this Mapper.

    The qoqa ID kept in the binding is the "id" of "items", renamed
    to ``item_id``
    """
    _model_name = 'qoqa.sale.order.line'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ('quantity', 'qoqa_quantity'),  # original quantity, without lot
              ('item_id', 'qoqa_id'),
              # TODO unit_price is for a LOT not UNITS!
              # divide by lot_size?
              # TODO: in scenario, flag taxes as tax incl.
              (qoqafloat('unit_price'), 'price_unit'),
              ]

    promo_products = {
        QOQA_PROMO_CUSTOMER_SERVICE: ('connector_ecommerce',
                                      'product_product_discount'),
        QOQA_PROMO_MARKETING: ('qoqa_base_data',
                               'product_product_marketing_coupon'),
        QOQA_PROMO_AFFILIATION: ('qoqa_base_data',
                                 'product_product_marketing_coupon'),
        QOQA_PROMO_STAFF: ('qoqa_base_data',
                           'product_product_marketing_coupon'),
    }

    def finalize(self, map_record, values):
        """ complete the values values from the 'item' sub-record """
        item = map_record.source['item']
        values.update({
            'custom_text': item['custom_text'],
            'qoqa_lot_size': item['lot_size'],
        })
        type_id = item['type_id']
        if type_id == QOQA_ITEM_PRODUCT:
            values.update(self._item_product(item))

        if type_id == QOQA_ITEM_SHIPPING:
            values.update(self._item_shipping(item, map_record.parent))

        elif type_id == QOQA_ITEM_DISCOUNT:
            values.update(self._item_discount(item, map_record.source['promo']))

        return values

    def _item_product(self, item):
        # qoqa.offer.position
        q_position_id = item['offer_id']
        binder = self.get_binder_for_model('qoqa.offer.position')
        position_id = binder.to_openerp(q_position_id)
        if position_id is None:
            raise MappingError("Offer Position with ID '%s' on QoQa has "
                               "not been imported, should have been imported "
                               "in _import_dependencies()." % q_position_id)
        # product.product
        binder = self.get_binder_for_model('qoqa.product.product')
        product_id = binder.to_openerp(item['variation_id'], unwrap=True)
        values = {'offer_position_id': position_id,
                  'product_id': product_id,
                  }
        return values

    def _item_shipping(self, item, parent):
        # find carrier_id from parent record (sales order)
        binder = self.get_binder_for_model('qoqa.offer')
        qdeal_id = parent.source['deal_id']
        offer_id = binder.to_openerp(qdeal_id, unwrap=True)
        if offer_id is None:
            raise MappingError("Offer with ID '%s' on QoQa has "
                               "not been imported, should have been imported "
                               "in _import_dependencies()." % qdeal_id)
        offer = self.session.browse('qoqa.offer', offer_id)
        # line builder
        builder = self.get_connector_unit_for_model(QoQaShippingLineBuilder)
        builder.price_unit = 0
        if offer.carrier_id:
            builder.carrier = offer.carrier_id
        values = builder.get_line()
        del values['price_unit']  # keep the price of the direct mapping
        return values

    def _item_discount(self, item, promo):
        # line builder
        builder = self.get_connector_unit_for_model(QoQaPromoLineBuilder)

        # choose product according to the promo type
        promo_type_id = promo['promo_type_id']
        product_ref = self.promo_products.get(promo_type_id)
        if product_ref is None:
            raise MappingError("Type of promo '%s' is not supported" %
                               promo_type_id)

        builder.price_unit = 0
        builder.product_ref = product_ref
        builder.code = item['promo_id']
        values = builder.get_line()
        del values['price_unit']  # keep the price of the direct mapping
        return values

    @mapping
    def quantity(self, record):
        """ Quantity is multiplied by the lot size:

        Example: a customer buy 2 x 6 bottles of wine: 12 units

        """
        quantity = record['quantity']
        lot_size = record['item']['lot_size'] or 1
        total = quantity * lot_size
        return {'product_uos_qty': total, 'product_uom_qty': total}


@qoqa
class LineMapChild(ImportMapChild):
    _model_name = 'qoqa.sale.order.line'

    def skip_item(self, map_record):
        record = map_record.source
        if not record['quantity']:
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


@qoqa
class QoQaShippingLineBuilder(ShippingLineBuilder):
    _model_name = 'qoqa.sale.order.line'

    def __init__(self, environment):
        super(QoQaShippingLineBuilder, self).__init__(environment)
        self.carrier = None

    def get_line(self):
        line = super(QoQaShippingLineBuilder, self).get_line()
        if self.carrier:
            line['product_id'] = self.carrier.product_id.id
            line['name'] = self.carrier.name
        return line


@qoqa
class QoQaPromoLineBuilder(SpecialOrderLineBuilder):
    _model_name = 'qoqa.sale.order.line'

    def __init__(self, environment):
        super(QoQaPromoLineBuilder, self).__init__(environment)
        # the sign is 1 because the API already provides a negative
        self.sign = 1
        self.code = None

    def get_line(self):
        line = super(QoQaPromoLineBuilder, self).get_line()
        if self.code:
            line['name'] = "%s (%s)" % (line['name'], self.code)
        return line
