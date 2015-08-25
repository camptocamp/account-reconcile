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

from __future__ import division
import math

from datetime import datetime, timedelta

from openerp.osv import orm, fields
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class qoqa_offer_position_variant(orm.Model):
    _name = 'qoqa.offer.position.variant'
    _description = 'QoQa Offer Position Variant'
    _order = 'sequence asc, id asc'

    def _get_stock(self, cr, uid, ids, fields, args, context=None):
        """Get number of products sold, remaining and the progress.

        :returns: fields value
        :rtype: dict
        """
        res = {}
        for variant in self.browse(cr, uid, ids, context=context):
            if not variant.exists():
                # when we delete a variant from a position, the trigger
                # will call the recompute also for the deleted variant,
                # so it would fail to compute for a missing record
                continue
            # the equivalent with the ORM takes up to 7 seconds
            cr.execute("SELECT SUM(l.product_uom_qty) "
                       "FROM sale_order_line l "
                       "INNER JOIN sale_order so "
                       "ON so.id = l.order_id "
                       "WHERE so.offer_id = %s "
                       "AND so.state NOT IN ('draft', 'cancel') "
                       "AND l.product_id = %s ",
                       (variant.position_id.offer_id.id,
                        variant.product_id.id))
            num_sold = cr.fetchone()[0] or 0
            quantity = variant.quantity
            residual = quantity - num_sold
            progress = 0.
            if quantity != 0:
                # progress bar is full when all is sold
                progress = ((quantity - residual) / quantity) * 100
            res[variant.id] = {
                'stock_sold': num_sold,
                'stock_residual': residual,
                'stock_progress': progress,
                'stock_progress_remaining': 100 - progress,
            }
        return res

    def _get_from_offer_position(self, cr, uid, ids, context=None):
        this = self.pool.get('qoqa.offer.position.variant')
        pos_variant_ids = this.search(
            cr, uid,
            [('position_id', 'in', ids)],
            context=context)
        return pos_variant_ids

    def _get_from_sale_order(self, cr, uid, ids, context=None):
        this = self.pool.get('qoqa.offer.position.variant')
        sale_obj = self.pool.get('sale.order')
        sales = sale_obj.read(cr, uid, ids, ['order_line'], context=context)

        line_ids = [lines for sale in sales for lines in sale['order_line']]
        return this._get_from_sale_order_line(
            cr, uid, line_ids, context=context)

    def _get_from_sale_order_line(self, cr, uid, ids, context=None):
        this = self.pool.get('qoqa.offer.position.variant')
        line_obj = self.pool.get('sale.order.line')
        lines = line_obj.read(cr, uid, ids,
                              ['offer_position_id', 'product_id'],
                              context=context)
        position_ids = []
        product_ids = []
        for line in lines:
            if line['offer_position_id']:
                position_ids.append(line['offer_position_id'][0])
            if line['product_id']:
                product_ids.append(line['product_id'][0])
        this_ids = this.search(
            cr, uid,
            [('position_id', 'in', position_ids),
             ('product_id', 'in', product_ids)],
            context=context)
        return this_ids

    def _get_from_position(self, cr, uid, ids, context=None):
        this = self.pool.get('qoqa.offer.position.variant')
        return this.search(cr, uid, [('position_id', 'in', ids)],
                           context=context)

    _progress_store = {
        _name: (lambda self, cr, uid, ids, context=None: ids, None, 10),
        # weirdly, field is not computed on the creation of the variant
        # if this trigger is not there
        'qoqa.offer.position': (_get_from_position, ['variant_ids'], 10),
        'sale.order': (_get_from_sale_order,
                       ['offer_id', 'order_line', 'state'], 10),
        'sale.order.line': (_get_from_sale_order_line,
                            ['product_id', 'product_uom_qty'], 10),
    }

    _columns = {
        'sequence': fields.integer('Sequence'),
        'position_id': fields.many2one(
            'qoqa.offer.position',
            string='Position',
            readonly=True,
            select=True,
            required=True,
            ondelete='cascade'),
        'product_id': fields.many2one(
            'product.product',
            string='Product',
            required=True,
            select=True,
            ondelete='restrict'),
        'quantity': fields.integer('Quantity', required=True),
        'stock_sold': fields.function(
            _get_stock,
            string='Sold',
            type='integer',
            multi='stock',
            store=_progress_store),
        'stock_residual': fields.function(
            _get_stock,
            string='Remaining',
            type='integer',
            multi='stock',
            store=_progress_store),
        'stock_progress': fields.function(
            _get_stock,
            string='Progress',
            type='float',
            multi='stock',
            store=_progress_store),
        'stock_progress_remaining': fields.function(
            _get_stock,
            string='Remaining (%)',
            type='float',
            multi='stock',
            store=_progress_store),
    }

    _defaults = {
        'sequence': 1,
    }


class qoqa_offer_position(orm.Model):
    _name = 'qoqa.offer.position'
    _description = 'QoQa Offer Position'
    _order = 'sequence asc'

    REGULAR_PRICE_TYPE = [('normal', 'Normal Price'),
                          ('no_price', 'No Price'),
                          ('direct', 'Direct Price'),
                          ]

    def _get_stock_values(self, cr, uid, ids, context=None):
        """Get stock values.

        This method only computes "offline values", that means
        the values computed using the OpenERP stock and sales.

        The connector_qoqa module inherit from this method and adds the
        "online values" logic: when an offer is in progress, the stock
        values are read from the QoQa API so they are realtime and
        thus more accurate.

        :returns: computed values
        :rtype: dict
        """
        res = {}
        for offer in self.browse(cr, uid, ids, context=context):
            quantity = 0
            residual = 0
            for variant in offer.variant_ids:
                quantity += variant.quantity
                residual += variant.stock_residual

            progress = 0.0
            if quantity > 0:
                progress = ((quantity - residual) / quantity) * 100

            res[offer.id] = {
                'sum_quantity': quantity,
                'sum_stock_sold': quantity - residual,
                'sum_residual': residual,
                'stock_progress': math.ceil(progress),
                'stock_progress_remaining': 100 - math.ceil(progress),
                # reserved stock is only accessible online, so
                # implemented in connector_qoqa, hidden when offline
                'stock_reserved': 0,
                'stock_reserved_percent': 0,
                # stock online fields are set in connector_qoqa
                'stock_is_online': False,
                'stock_online_failure': False,
                'stock_online_failure_message': '',
            }
        return res

    def _get_stock(self, cr, uid, ids, fields, args, context=None):
        return self._get_stock_values(cr, uid, ids, context=context)

    def _get_image(self, cr, uid, ids, fieldnames, args, context=None):
        res = {}
        for position in self.browse(cr, uid, ids, context=context):
            res[position.id] = {'image_small': False,
                                'image_medium': False}
            for variant in position.variant_ids:
                product = variant.product_id
                small = product.image_small
                # if we have the small image, we have the medium too
                # as they are all build from the same image
                if small:
                    res[position.id]['image_small'] = small
                    res[position.id]['image_medium'] = product.image_medium
                break
        return res

    def _get_lot_price(self, cr, uid, ids, fieldnames, args, context=None):
        res = {}
        for position in self.browse(cr, uid, ids, context=context):
            res[position.id] = position.unit_price * position.lot_size
        return res

    _columns = {
        'offer_id': fields.many2one(
            'qoqa.offer',
            string='Offer',
            readonly=True,
            select=True,
            required=True),
        'variant_ids': fields.one2many(
            'qoqa.offer.position.variant',
            'position_id',
            string='Variants'),
        'image_small': fields.function(
            _get_image,
            string='Thumbnail',
            type='binary',
            readonly=True,
            multi='_get_image'),
        'image_medium': fields.function(
            _get_image,
            string='Medium-sized Image',
            type='binary',
            readonly=True,
            multi='_get_image'),
        'sequence': fields.integer('Sequence',
                                   help="The first position is the main one"),
        'product_tmpl_id': fields.many2one(
            'product.template',
            string='Product Template',
            required=True),
        'currency_id': fields.related(
            'offer_id', 'pricelist_id', 'currency_id',
            type='many2one',
            relation='res.currency',
            string='Currency',
            readonly=True),
        'highlights': fields.text('Highlights', readonly=True, translate=True),
        'description': fields.html('Description',
                                   readonly=True,
                                   translate=True),
        # only 1 tax is used on the QoQa backend, so we
        # have to choose only 1 for the position, the field
        # will also keep the reference to the historical tax
        # if the product's taxes change
        'tax_id': fields.many2one(
            'account.tax',
            string='Tax',
            required=True,
            domain=[('type_tax_use', 'in', ('sale', 'all')),
                    ('ecotax', '=', False)]),
        'lot_size': fields.integer('Lot Size', required=True),
        'max_sellable': fields.integer('Max Sellable', required=True),
        'stock_bias': fields.related(
            'offer_id', 'stock_bias',
            string='Stock Bias',
            readonly=True),
        'current_unit_price': fields.related(
            'product_tmpl_id', 'list_price',
            string="Product Price at Date",
            type='float',
            help="The price of the product at the beginning date of the "
                 "offer. It will be modified directly on the product.",
            digits_compute=dp.get_precision('Product Price')),
        'unit_price': fields.float(
            string='Unit Price',
            digits_compute=dp.get_precision('Product Price'),
            readonly=True),
        'lot_price': fields.float(
            string='Lot Price',
            digits=(16, 2),
            readonly=True),
        'installment_price': fields.float(
            'Installment Price',
            digits_compute=dp.get_precision('Product Price'),
            readonly=True),
        'regular_price': fields.float(
            'Regular Price',
            digits_compute=dp.get_precision('Product Price'),
            required=True),
        'regular_price_type': fields.selection(
            REGULAR_PRICE_TYPE,
            string='Regular Price Type',
            required=True),
        'buy_price': fields.float(
            'Buy Price',
            digits_compute=dp.get_precision('Product Price')),
        'top_price': fields.float(
            'Top Price',
            digits_compute=dp.get_precision('Product Price')),
        'date_delivery': fields.date(
            'Delivery Date',
            help="Maximum delivery date for customer. This information is "
                 "displayed in the customer account"),
        'booking_delivery': fields.boolean('Booking Delivery'),
        'buyphrase_id': fields.many2one('qoqa.buyphrase',
                                        string='Buyphrase'),
        'order_url': fields.char('Order URL'),
        'stock_is_online': fields.function(
            _get_stock,
            string="Online Stock",
            type='boolean',
            multi='stock',
            help="The stock displays the real online values when "
                 "the offer is underway."),
        'stock_online_failure': fields.function(
            _get_stock,
            string="Online Failure",
            type='boolean',
            multi='stock',
            help="Failed to get the online stock, probably a network "
                 "failure. Please retry."),
        'stock_online_failure_message': fields.function(
            _get_stock,
            string="Stock Online Error",
            type='text',
            multi='stock'),
        'sum_quantity': fields.function(
            _get_stock,
            string='Quantity',
            type='integer',
            multi='stock'),
        'sum_stock_sold': fields.function(
            _get_stock,
            string='Sold',
            type='integer',
            multi='stock'),
        'sum_residual': fields.function(
            _get_stock,
            string='Residual',
            type='integer',
            multi='stock'),
        'stock_progress': fields.function(
            _get_stock,
            string='Progress',
            type='integer',
            multi='stock'),
        'stock_progress_remaining': fields.function(
            _get_stock,
            string='Remaining (%)',
            type='integer',
            multi='stock'),
        'stock_reserved': fields.function(
            _get_stock,
            string='Reserved (online)',
            type='integer',
            multi='stock'),
        'stock_reserved_percent': fields.function(
            _get_stock,
            string='Reserved (%) (online)',
            type='integer',
            multi='stock'),
        'active': fields.boolean('Active'),
        # kept for import of historic deals
        'poste_cumbersome_package': fields.boolean(
            'Poste Cumbersome Package'),
    }

    def _default_date_delivery(self, cr, uid, context=None):
        fmt = DEFAULT_SERVER_DATE_FORMAT
        return (datetime.now() + timedelta(days=15)).strftime(fmt)

    _defaults = {
        'regular_price_type': 'normal',
        'max_sellable': 3,
        'lot_size': 1,
        'active': 1,
        'date_delivery': _default_date_delivery,
    }

    _sql_constraints = [
        ('lot_size', 'check (lot_size > 0)',
         'Lot size must be a value greater than 0.'),
        ('lot_price', 'check (lot_price >= 0)',
         'Lot price must be a value greater or equal to 0.'),
    ]

    @staticmethod
    def _history_price_date(offer):
        date_fmt = DEFAULT_SERVER_DATE_FORMAT
        datetime_fmt = DEFAULT_SERVER_DATETIME_FORMAT
        begin = datetime.strptime(offer.date_begin, date_fmt)
        begin += timedelta(hours=offer.time_begin)
        return begin.strftime(datetime_fmt)

    def create(self, cr, uid, vals, context=None):
        price = vals.get('current_unit_price') or 0
        lot_size = vals.get('lot_size') or 1
        vals = vals.copy()
        vals.update({
            'unit_price': price,
            'lot_price': price * lot_size,
        })
        if vals.get('offer_id'):
            offer_obj = self.pool['qoqa.offer']
            offer = offer_obj.browse(cr, uid, vals['offer_id'],
                                     context=context)
            context = context.copy()
            context['to_date'] = self._history_price_date(offer)
        res = super(qoqa_offer_position, self).\
            create(cr, uid, vals, context=context)

        # workaround: the related does not write the new price
        # on the product template when we create the record, so
        # do it manually
        if 'current_unit_price' in vals:
            tmpl_id = vals['product_tmpl_id']
            tmpl_obj = self.pool['product.template']
            tmpl_obj.write(cr, uid, [tmpl_id],
                           {'list_price': price},
                           context=context)
        if vals.get('date_delivery'):
            self.check_date(cr, uid, vals['date_delivery'],
                            context=context)
        return res

    def check_date(self, cr, uid, current_date, context=None):
        context_today = fields.date.context_today(self, cr, uid,
                                                  context=context)
        if current_date < context_today:
            raise orm.except_orm(
                _('Error'),
                _('You cannot select a delivery date in the past'))
        else:
            return True

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        if self.browse(cr, uid, id, context=context).date_delivery:
            fmt = DEFAULT_SERVER_DATE_FORMAT
            context_today = fields.date.context_today(self, cr, uid,
                                                      context=context)
            today = datetime.strptime(context_today, fmt)
            today_plus_15_days = today + timedelta(days=15)
            default.update({
                'date_delivery': today_plus_15_days.strftime(fmt),
            })
        return super(qoqa_offer_position, self).copy_data(
            cr, uid, id, default=default, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        if vals.get('date_delivery'):
            # We will check that the delivery date is not in the pas
            for position in self.browse(cr, uid, ids, context=context):
                self.check_date(cr, uid, vals['date_delivery'],
                                context=context)

        if 'current_unit_price' in vals or 'lot_size' in vals:
            for position in self.browse(cr, uid, ids, context=context):
                offer_obj = self.pool['qoqa.offer']
                if vals.get('offer_id'):
                    offer = offer_obj.browse(cr, uid, vals['offer_id'],
                                             context=context)
                else:
                    offer = position.offer_id

                ctx = context.copy()
                ctx['to_date'] = self._history_price_date(offer)

                if 'current_unit_price' in vals:
                    price = vals['current_unit_price']
                else:
                    price = position.current_unit_price
                if 'lot_size' in vals:
                    lot_size = vals['lot_size']
                else:
                    lot_size = position.lot_size
                local_vals = vals.copy()
                local_vals.update({
                    'unit_price': price,
                    'lot_price': price * lot_size
                })
                super(qoqa_offer_position, self).\
                    write(cr, uid, [position.id], local_vals, context=ctx)
            return True
        else:
            return super(qoqa_offer_position, self).\
                write(cr, uid, ids, vals, context=context)

    def onchange_product_tmpl_id(self, cr, uid, ids, product_tmpl_id,
                                 lot_size, date_begin, time_begin,
                                 context=None):
        """ Automatically adds all the variants of the template and
        set sensible default values for some fields.

        It does not uses the pricelist to get the price as they are based
        on the products and not the templates.

        When it defines the tax for the position, it takes the tax configured
        on the template, but leaves the field empty if the product has several
        taxes (as of today, only 1 tax is supported on the QoQa backend).
        """
        if context is None:
            context = {}
        res = {'value': {}}
        if not product_tmpl_id:
            return res
        template_obj = self.pool.get('product.template')
        if ids:
            assert len(ids) == 1
            position = self.browse(cr, uid, ids[0], context=context)
        else:
            position = None

        context = context.copy()
        context.update({
            'date_begin': date_begin,
            'time_begin': time_begin,
        })
        template = template_obj.browse(cr, uid, product_tmpl_id,
                                       context=context)

        buy_price = \
            template.seller_ids and \
            template.seller_ids[0].pricelist_ids and \
            template.seller_ids[0].pricelist_ids[0].price or \
            0.0

        values = {
            'current_unit_price': template.list_price,
            'buy_price': buy_price,
        }

        # do not refresh the taxes and variants if the template has not
        # been modified, but something has been changed on the product
        if not position or position.product_tmpl_id.id != product_tmpl_id:
            tax_ids = [tax.id for tax in template.taxes_id if not tax.ecotax]
            lines = [{'product_id': variant.id, 'quantity': 1}
                     for variant
                     in sorted(template.variant_ids,
                               key=lambda variant: variant.variants)
                     ]
            values.update({
                'variant_ids': lines,
                'tax_id': tax_ids[0] if len(tax_ids) == 1 else False,
            })
        res['value'] = values
        return res

    def onchange_current_price(self, cr, uid, ids, current_unit_price,
                               lot_size, context=None):
        res = {'value': {}}
        values = {
            'unit_price': current_unit_price,
            'lot_price': current_unit_price * lot_size,
        }
        res['value'] = values
        return res
