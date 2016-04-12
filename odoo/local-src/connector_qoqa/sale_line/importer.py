# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import division
import logging

from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  ImportMapChild,
                                                  )
# from openerp.addons.connector_ecommerce.sale import (ShippingLineBuilder,
#                                                      SpecialOrderLineBuilder,
#                                                      )
from ..backend import qoqa

_logger = logging.getLogger(__name__)


class QoQaLineCategory(object):
    product = 'product'
    # TODO: check
    discount = 'discount'
    shipping = 'shipping'
    service = 'service'


@qoqa
class SaleOrderLineImportMapper(ImportMapper):
    """ Convert 'order_items' and 'items' into sales order lines.

    The 2 dicts are merged, then passed to this Mapper.

    The qoqa ID kept in the binding is the "id" of "items", renamed
    to ``item_id``
    """
    _model_name = 'qoqa.sale.order.line'

    # TODO discount_id
    # TODO: set delay as (delivery_date - date.today()).days

    direct = [('lot_quantity', 'qoqa_quantity'),  # original quantity on lot
              ('id', 'qoqa_id'),
              ]

    def finalize(self, map_record, values):
        """ complete the values values from the 'item' sub-record """
        line = map_record.source
        category = line['category']
        if category == QoQaLineCategory.product:
            values.update(self._item_product(line))

        if category == QoQaLineCategory.shipping:
            values.update(self._item_shipping(line, map_record.parent))

        elif category == QoQaLineCategory.discount:
            values.update(self._item_discount(line,
                                              map_record.source['promo']))

        return values

    def _item_product(self, line):
        qoqa_variant_id = line['offer_variation_id']
        binder = self.binder_for('qoqa.product.product')
        product = binder.to_openerp(qoqa_variant_id, unwrap=True)
        if not product:
            raise MappingError('product variant with QoQa Id %s does not '
                               'exist in Odoo' % qoqa_variant_id)
        return {'product_id': product.id}

    # TODO: ask if lines of type shipping still exist
    def _item_shipping(self, line, parent):
        # find carrier_id from parent record (sales order)
        binder = self.binder_for('qoqa.shipper.rate')
        qoqa_fee_id = parent.source['data']['attributes']['shipping_fee_id']
        fee = binder.to_openerp(qoqa_fee_id, unwrap=True)
        if fee:
            raise MappingError("Shipping fee with id %s "
                               "does not exist. Please create it." %
                               qoqa_fee_id)
        # line builder
        builder = self.unit_for(QoQaShippingLineBuilder)
        builder.price_unit = 0
        builder.quantity = line['lot_quantity']
        # this is the delivery carrier having the rates
        builder.carrier = fee
        values = builder.get_line()
        del values['price_unit']  # keep the price of the mapping
        return values

    def _promo_type(self, promo):
        qpromo_type_id = promo['promo_type_id']
        promo_binder = self.binder_for('qoqa.promo.type')
        promo_type = promo_binder.to_openerp(qpromo_type_id)
        if not promo_type:
            raise MappingError("Type of promo '%s' is not supported." %
                               qpromo_type_id)
        return promo_type

    def _item_discount(self, line, promo):
        # line builder
        builder = self.unit_for(QoQaPromoLineBuilder)
        promo_type = self._promo_type(promo)
        builder.price_unit = 0
        # choose product according to the promo type
        builder.product = promo_type.product_id
        builder.code = line['promo_id']
        values = builder.get_line()
        del values['price_unit']  # keep the price of the mapping
        return values

    # TODO: check if quantity is still as units or as lots
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
        lot_size = record['lot_size'] or 1
        quantity = record['lot_quantity']
        price = float(record['unit_price'])
        if lot_size > 1:
            price /= lot_size
        values = {'product_uos_qty': quantity,
                  'product_uom_qty': quantity,
                  'price_unit': price}
        return values


@qoqa
class LineMapChild(ImportMapChild):
    _model_name = 'qoqa.sale.order.line'

    def skip_item(self, map_record):
        record = map_record.source
        if not record['lot_quantity']:
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


# @qoqa
# class QoQaShippingLineBuilder(ShippingLineBuilder):
#     _model_name = 'qoqa.sale.order.line'

#     def __init__(self, environment):
#         super(QoQaShippingLineBuilder, self).__init__(environment)
#         self.carrier = None

#     def get_line(self):
#         line = super(QoQaShippingLineBuilder, self).get_line()
#         if self.carrier:
#             line['product_id'] = self.carrier.product_id.id
#             line['name'] = self.carrier.name
#         return line


# @qoqa
# class QoQaPromoLineBuilder(SpecialOrderLineBuilder):
#     _model_name = 'qoqa.sale.order.line'

#     def __init__(self, environment):
#         super(QoQaPromoLineBuilder, self).__init__(environment)
#         # the sign is 1 because the API already provides a negative
#         self.sign = 1
#         self.code = None

#     def get_line(self):
#         line = super(QoQaPromoLineBuilder, self).get_line()
#         if self.code:
#             line['name'] = "%s (%s)" % (line['name'], self.code)
#         return line
