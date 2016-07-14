# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import division
import logging

from datetime import date

from openerp import fields
from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  ImportMapChild,
                                                  )
from openerp.addons.connector_ecommerce.unit.line_builder import (
    ShippingLineBuilder,
    SpecialOrderLineBuilder,
    )
from ..backend import qoqa
from ..connector import iso8601_to_local_date
from ..unit.mapper import FromAttributes

_logger = logging.getLogger(__name__)


class QoQaLineCategory(object):
    product = 'product'
    discount = 'discount'
    shipping = 'shipping'
    service = 'service'


@qoqa
class SaleOrderLineImportMapper(ImportMapper, FromAttributes):
    """ Convert 'order_items' and 'items' into sales order lines.

    The 2 dicts are merged, then passed to this Mapper.

    The qoqa ID kept in the binding is the "id" of "items", renamed
    to ``item_id``
    """
    _model_name = 'qoqa.sale.order.line'

    from_attributes = [
        ('lot_quantity', 'qoqa_quantity'),  # original quantity on lot
        ('id', 'qoqa_id'),
    ]

    def finalize(self, map_record, values):
        """ complete the values values from the 'item' sub-record """
        line = map_record.source
        category = line['attributes']['category']
        if category == QoQaLineCategory.product:
            values.update(self._item_product(line))

        if category == QoQaLineCategory.shipping:
            values.update(self._item_shipping(line, map_record.parent))

        elif category == QoQaLineCategory.discount:
            discount_id = map_record.source['attributes']['discount_id']
            discount = self._find_discount(map_record, discount_id)
            values.update(self._item_discount(line, discount))

        order = map_record.parent.source
        date_delivery = order['data']['attributes']['delivery_on']
        if date_delivery:
            date_delivery = iso8601_to_local_date(date_delivery)
            delivery_date = fields.Date.from_string(date_delivery)
            today = date.today()
            values['delay'] = (delivery_date - today).days

        return values

    def _find_discount(self, map_record, discount_id):
        order_included = map_record.parent.source['included']
        discounts = [item for item in order_included
                     if item['type'] == 'discount' and
                     item['id'] == str(discount_id)]
        if not discounts:
            raise MappingError('Missing data for discount %s' % discount_id)
        return discounts[0]

    def _item_product(self, line):
        qoqa_variant_id = line['attributes']['variation_id']
        binder = self.binder_for('qoqa.product.product')
        product = binder.to_openerp(qoqa_variant_id, unwrap=True)
        if not product:
            raise MappingError('product variant with QoQa Id %s does not '
                               'exist in Odoo' % qoqa_variant_id)
        return {'product_id': product.id}

    def _item_shipping(self, line, parent):
        # find carrier_id from parent record (sales order)
        binder = self.binder_for('qoqa.shipper.fee')
        qoqa_fee_id = parent.source['data']['attributes']['shipping_fee_id']
        fee = binder.to_openerp(qoqa_fee_id, unwrap=True)
        if not fee:
            raise MappingError("Shipping fee with id %s "
                               "does not exist. Please create it." %
                               qoqa_fee_id)
        # line builder
        builder = self.unit_for(QoQaShippingLineBuilder)
        builder.price_unit = 0
        builder.quantity = line['attributes']['lot_quantity']
        # this is the delivery carrier having the rates
        builder.carrier = fee
        builder.product = fee.product_id
        values = builder.get_line()
        del values['price_unit']  # keep the price of the mapping
        return values

    def _discount_type(self, discount):
        attrs = discount['attributes']
        sub_type = attrs['sub_type']
        promo_binder = self.binder_for('qoqa.promo.type')
        promo_type = promo_binder.to_openerp(sub_type)
        if not promo_type:
            raise MappingError("Type of discount '%s' is not supported." %
                               sub_type)
        return promo_type

    def _item_discount(self, line, discount):
        # line builder
        builder = self.unit_for(QoQaPromoLineBuilder)
        promo_type = self._discount_type(discount)
        builder.price_unit = -float(line['attributes']['unit_price'])
        # choose product according to the promo type
        builder.product = promo_type.product_id
        builder.code = discount['id']
        values = builder.get_line()
        values.update({
            'discount_code_name': discount['id'],
            'discount_description': discount['attributes']['description'],
        })
        return values

    @mapping
    def quantity(self, record):
        """ Return the quantity and the unit price

        Example: a customer buy 2 x 6 bottles of wine: 12 units.
        The lot size here is 2. QoQa gives the quantity as units,
        but it gives the price of a lot.

        The unit price on QoQa is the price for a *lot*.
        We want the price for a *unit*. We divide the price
        by the lot size.  The decimal precision of the products
        should be 3 digits to ensure we do not lose precision.

        """
        attributes = record['attributes']
        lot_size = attributes['lot_size'] or 1
        quantity = attributes['lot_quantity']
        price = float(attributes['unit_price'])
        if lot_size > 1:
            price /= lot_size
        values = {'product_uom_qty': quantity,
                  'price_unit': price}
        return values


@qoqa
class LineMapChild(ImportMapChild):
    _model_name = 'qoqa.sale.order.line'

    def skip_item(self, map_record):
        record = map_record.source
        if not record['attributes']['lot_quantity']:
            return True

    def get_item_values(self, map_record, to_attr, options):
        values = map_record.values(**options)
        binder = self.binder_for()
        binding = binder.to_openerp(map_record.source['id'])
        if binding:
            # already exists, keeps the id
            values['id'] = binding.id
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
