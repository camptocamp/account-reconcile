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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp
from .qoqa_offer import qoqa_offer


class qoqa_offer_position_variant(orm.Model):
    _name = 'qoqa.offer.position.variant'
    _description = 'QoQa Offer Position Variant'

    def _get_stock(self, cr, uid, ids, fields, args, context=None):
        """Get number of products sold, remaining and the progress.

        :returns: fields value
        :rtype: dict
        """
        res = {}
        sale_line_obj = self.pool.get('sale.order.line')
        for variant in self.browse(cr, uid, ids, context=context):
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
            # Example: we sell 500 lot of 6 bottles of wine. 1 bottle =
            # 1 unit. In the sales orders, 1 lot will be expanded to 6 units.
            # So we compare lots, not units.
            lot_size = variant.position_id.lot_size
            num_sold /= lot_size
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

    def _get_from_offer(self, cr, uid, ids, context=None):
        this = self.pool.get('qoqa.offer.position.variant')
        pos_variant_ids = this.search(
            cr, uid,
            [('position_id.offer_id', 'in', ids)],
            context=context)
        return pos_variant_ids

    def _get_from_sale_order(self, cr, uid, ids, context=None):
        this = self.pool.get('qoqa.offer.position.variant')
        sale_obj = self.pool.get('sale.order')
        sales = sale_obj.read(cr, uid, ids, ['offer_id'], context=context)
        offer_ids = [sale['offer_id'][0] for sale in sales
                     if sale['offer_id']]
        return this._get_from_offer(cr, uid, offer_ids, context=context)

    def _get_from_sale_order_line(self, cr, uid, ids, context=None):
        this = self.pool.get('qoqa.offer.position.variant')
        line_obj = self.pool.get('sale.order.line')
        lines = line_obj.read(cr, uid, ids, ['offer_position_id'],
                              context=context)
        offer_ids = [line['offer_position_id'][0] for line in lines
                     if line['offer_position_id']]
        return this._get_from_offer(cr, uid, offer_ids, context=context)

    _progress_store = {
        _name: (lambda self, cr, uid, ids, context=None: ids, None, 10),
        'qoqa.offer.position': (_get_from_offer_position, ['lot_size'], 10),
        'sale.order': (_get_from_sale_order,
                       ['offer_id', 'order_line', 'state'], 10),
        'sale.order.line': (_get_from_sale_order_line,
                            ['product_id', 'product_uom_qty'], 10),
    }

    _columns = {
        'position_id': fields.many2one(
            'qoqa.offer.position',
            string='Position',
            readonly=True,
            required=True,
            ondelete='cascade'),
        'product_id': fields.many2one(
            'product.product',
            string='Product',
            required=True,
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


class qoqa_offer_position(orm.Model):
    _name = 'qoqa.offer.position'
    _description = 'QoQa Offer Position'
    _order = 'sequence asc'

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
                'stock_progress': progress,
                'stock_progress_remaining': 100 - progress,
            }
        return res

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

    _columns = {
        'offer_id': fields.many2one(
            'qoqa.offer',
            string='Offer',
            readonly=True,
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
        # kept so we can migrate the data, can be removed after
        # half-2014
        'ecotax': fields.integer('Ecotax', deprecated=True),
        'ecotax_id': fields.many2one(
            'account.tax',
            string='Ecotax',
            domain=[('type_tax_use', 'in', ('sale', 'all')),
                    ('ecotax', '=', True)]),
        'date_delivery': fields.date('Delivery Date'),
        'booking_delivery': fields.boolean('Booking Delivery'),
        'buyphrase_id': fields.many2one('qoqa.buyphrase',
                                        string='Buyphrase'),
        'order_url': fields.char('Order URL'),
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
            type='float',
            multi='stock'),
        'stock_progress_remaining': fields.function(
            _get_stock,
            string='Remaining (%)',
            type='float',
            multi='stock'),
        'active': fields.boolean('Active'),
        # kept for import of historic deals
        'poste_cumbersome_package': fields.boolean(
            'Poste Cumbersome Package'),
    }

    _defaults = {
        'regular_price_type': 'normal',
        'max_sellable': 3,
        'lot_size': 1,
        'active': 1,
    }

    _sql_constraints = [
        ('lot_size', 'CHECK (lot_size>0)',
         'Lot size must be a value greater than 0.'),
    ]

    def onchange_product_tmpl_id(self, cr, uid, ids, product_tmpl_id,
                                 context=None):
        """ Automatically adds all the variants of the template and
        set sensible default values for some fields.

        It does not uses the pricelist to get the price as they are based
        on the products and not the templates.

        When it defines the tax for the position, it takes the tax configured
        on the template, but leaves the field empty if the product has several
        taxes (as of today, only 1 tax is supported on the QoQa backend).
        """
        res = {'value': {}}
        if not product_tmpl_id:
            return res
        template_obj = self.pool.get('product.template')
        template = template_obj.browse(cr, uid, product_tmpl_id,
                                       context=context)
        tax_ids = []
        ecotax_ids = []
        for tax in template.taxes_id:
            if tax.ecotax:
                ecotax_ids.append(tax.id)
            else:
                tax_ids.append(tax.id)

        lines = [{'product_id': variant.id, 'quantity': 1} for
                 variant in template.variant_ids]
        values = {
            'variant_ids': lines,
            'unit_price': template.list_price,
            'buy_price': template.standard_price,
            'tax_id': tax_ids[0] if len(tax_ids) == 1 else False,
            'ecotax_id': ecotax_ids[0] if len(ecotax_ids) == 1 else False,
        }
        res['value'] = values
        return res
