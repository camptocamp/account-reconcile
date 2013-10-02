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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp
from .qoqa_deal import qoqa_deal


class qoqa_deal_position_variant(orm.Model):
    _name = 'qoqa.deal.position.variant'
    _description = 'QoQa Deal Position Variant'

    def _get_stock(self, cr, uid, ids, fields, args, context=None):
        """Get number of products sold, remaining and the progress.

        :returns: fields value
        :rtype: dict
        """
        res = {}
        sale_line_obj = self.pool.get('sale.order.line')
        for variant in self.browse(cr, uid, ids, context=context):
            product_ids = sale_line_obj.search(
                cr, uid,
                [('product_id', '=', variant.product_id.id),
                 ('order_id.deal_id', '=', variant.position_id.deal_id.id)],
                context=context)
            sales_lines = sale_line_obj.browse(cr, uid, product_ids,
                                               context=context)
            num_sold = sum([line.product_uom_qty for line
                            in sales_lines
                            if line.order_id.state not in ['draft', 'cancel']])
            quantity = variant.quantity
            residual = quantity - num_sold
            progress = 0.0
            if quantity != 0:
                progress = ((quantity - residual) / quantity) * 100
            res[variant.id] = {
                'stock_sold': num_sold,
                'stock_residual': residual,
                'stock_progress': progress,
            }
        return res

    _columns = {
        'position_id': fields.many2one(
            'qoqa.deal.position',
            string='Position',
            readonly=True,
            required=True,
            ondelete='cascade'),
        'product_id': fields.many2one(
            'product.product',
            string='Product',
            required=True,
            domain="",
            ondelete='restrict'),
        'quantity': fields.integer('Quantity', required=True),
        'stock_sold': fields.function(
            _get_stock,
            string='Sold',
            type='integer',
            multi='stock'),
        'stock_residual': fields.function(
            _get_stock,
            string='Remaining',
            type='integer',
            multi='stock'),
        'stock_progress': fields.function(
            _get_stock,
            string='Progress',
            type='float',
            multi='stock'),
    }


# TODO rename to qoqa.deal.position
class qoqa_deal_position(orm.Model):
    _name = 'qoqa.deal.position'
    _description = 'QoQa Deal Position'

    REGULAR_PRICE_TYPE = [('normal', 'Normal Price'),
                          ('no_price', 'No Price'),
                          ('direct', 'Direct Price'),
                          ]

    def _get_stock(self, cr, uid, ids, fields, args, context=None):
        """Get stock numbers

        :returns: computed values
        :rtype: dict
        """
        res = {}

        for deal in self.browse(cr, uid, ids, context=context):
            quantity = 0
            residual = 0
            for variant in deal.variant_ids:
                quantity += variant.quantity
                residual += variant.stock_residual

            progress = 0.0
            if quantity > 0:
                progress = ((quantity - residual) / quantity) * 100

            res[deal.id] = {
                'sum_quantity': quantity,
                'sum_stock_sold': quantity - residual,
                'stock_progress': progress,
            }
        return res

    _columns = {
        'deal_id': fields.many2one(
            'qoqa.deal',
            string='Deal',
            readonly=True,
            required=True),
        'variant_ids': fields.one2many(
            'qoqa.deal.position.variant',
            'position_id',
            string='Variants'),
        'state': fields.related(
            'deal_id', 'state',
            string='State',
            type='selection',
            selection=qoqa_deal.DEAL_STATES,
            readonly=True),
        'sequence': fields.integer('Sequence',
                                   help="The first position is the main one"),
        'product_tmpl_id': fields.many2one(
            'product.template',
            string='Product Template',
            states={'draft': [('readonly', False)]},
            required=True),
        'currency_id': fields.related(
            'deal_id', 'pricelist_id', 'currency_id',
            type='many2one',
            relation='res.currency',
            string='Currency',
            readonly=True),
        # TODO: remove? use vat of product
        'vat_id': fields.many2one(
            'account.tax',
            string='VAT',
            required=True,
            domain="[('type_tax_use', '=', 'sale')]"),
        'lot_size': fields.integer('Lot Size', required=True),
        'max_sellable': fields.integer('Max Sellable', required=True),
        'stock_bias': fields.integer('Stock Bias'),
        'unit_price': fields.float(
            'Unit Price',
            digits_compute=dp.get_precision('Product Price'),
            required=True),
        'installment_price': fields.float(
            'Installment Price',
            digits_compute=dp.get_precision('Product Price')),
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
        'ecotax': fields.integer('Ecotax'),
        'date_delivery': fields.date('Delivery Date'),
        'booking_delivery': fields.boolean('Booking Delivery'),
        # TODO: many2one with phrases
        #'buyphrase_id': 
        'order_url': fields.char('Order URL'),
        'is_net_price': fields.boolean('Is Net Price'),

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
        'stock_progress': fields.function(
            _get_stock,
            string='Progress',
            type='float',
            multi='stock'),
    }

    _defaults = {
        'regular_price_type': 'normal',
        'stock_bias': 100,
    }

    def onchange_product_tmpl_id(self, cr, uid, ids, product_tmpl_id,
                                 context=None):
        """ Automatically adds all the variants of the template """
        res = {'value': {}}
        product_obj = self.pool.get('product.product')
        tmpl_variant_ids = product_obj.search(
            cr, uid,
            [('product_tmpl_id', '=', product_tmpl_id)],
            context=context)
        lines = [{'product_id': variant_id} for variant_id in tmpl_variant_ids]
        res['value']['variant_ids'] = lines
        return res
