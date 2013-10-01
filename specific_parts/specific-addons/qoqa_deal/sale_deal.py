# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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
import time

import openerp.addons.decimal_precision as dp
from openerp.osv import orm, fields


class qoqa_deal_variant(orm.Model):
    _name = 'qoqa.deal.variant'
    _description = 'QoQa Deal Variant'

    def _get_stock(self, cr, uid, ids, fields, args, context=None):
        """Get number of products sold, remaining and the progress.

        :returns: fields value
        :rtype: dict
        """
        res = {}
        sale_line_obj = self.pool.get('sale.order.line')
        for variant in self.browse(cr, uid, ids, context=context):
            # XXX base search on deal_id
            product_ids = sale_line_obj.search(
                cr, uid,
                [('product_id', '=', variant.product_id.id)],
                context=context)
            sold_products = sale_line_obj.browse(cr, uid, product_ids,
                                                 context=context)
            num_sold = sum([line.product_uom_qty for line
                            in sold_products
                            if line.order_id.state not in ['draft', 'cancel']])
            residual = (variant.stock_available -
                        variant.stock_reserved -
                        num_sold)

            progress = 0.0
            if variant.stock_available > 0:
                progress = ((variant.stock_available - residual) /
                            variant.stock_available) * 100

            res[variant.id] = {
                'stock_sold': num_sold,
                'stock_residual': residual,
                'stock_progress': progress,
            }

        return res

    _columns = {
        'deal_id': fields.many2one(
            'qoqa.deal',
            string='Deal',
            required=True,
            ondelete='cascade'),
        'product_id': fields.many2one(
            'product.product',
            string='Product',
            required=True,
            domain="[('product_tmpl_id', '=', product_tmpl_id)]",
            ondelete='cascade'),
        'sequence': fields.integer('Sequence'),
        'stock_available': fields.integer('Quantity on Hand'),
        'stock_reserved': fields.integer('Reserved'),

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


class qoqa_deal(orm.Model):
    _name = 'qoqa.deal'
    _description = 'QoQa Deal'
    _inherit = ['mail.thread']

    _order = 'date_begin'

    def _get_stock(self, cr, uid, ids, fields, args, context=None):
        """Get stock numbers

        :returns: computed values
        :rtype: dict
        """
        res = {}

        for deal in self.browse(cr, uid, ids, context=context):
            available = 0
            residual = 0
            for variant in deal.variant_ids:
                available += variant.stock_available
                residual += variant.stock_residual

            progress = 0.0
            if available > 0:
                progress = ((available - residual) / available) * 100

            res[deal.id] = {
                'sum_stock_available': available,
                'sum_stock_sold': available - residual,
                'stock_progress': progress,
            }
        return res

    def _day_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            # FIXME use proper methods for dates
            res[obj.id] = time.strftime('%Y-%m-%d', time.strptime(obj.date_begin, '%Y-%m-%d %H:%M:%S'))
        return res

    # XXX delete ?
    def _month_compute(self, cr, uid, ids, fieldnames, args, context=None):
        res = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            # FIXME use proper methods for dates
            res[obj.id] = time.strftime('%Y-%m', time.strptime(obj.date_begin, '%Y-%m-%d %H:%M:%S'))
        return res

    _columns = {
        'name': fields.char('Deal Reference', required=True),
        'description': fields.text('Description', translate=True),
        'product_tmpl_id': fields.many2one(
            'product.template',
            string='Product',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]},
            ondelete='set null',
            select=True),
        'variant_ids': fields.one2many(
            'qoqa.deal.variant',
            'deal_id',
            'Variants'),
        'date_begin': fields.datetime(
            'Start Date',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'date_end': fields.datetime(
            'End Date',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]}),

        'day': fields.function(
            _day_compute,
            type='char',
            string='Day',
            store=True,
            select=1,
            size=32),
        'month': fields.function(
            _month_compute,
            type='char',
            string='Month',
            store=True,
            select=1,
            size=32),

        # TODO replace by a m2o to a qoqa.backend
        'site': fields.selection(
            [('qoqa', 'QoQa'),
             ('qwine', 'QWine'),
             ('qstyle', 'QStyle'),
             ('qsport', 'QSport')],
            string='Sell on',
            required=True),
        'price_sale': fields.float(
            'Sale Price',
            required=True,
            digits_compute=dp.get_precision('Product Price')),
        'price_recommended': fields.float(
            'Recommended Price',
            required=True,
            digits_compute=dp.get_precision('Product Price')),
        'price_observed': fields.float(
            'Observed Price',
            required=True,
            digits_compute=dp.get_precision('Product Price')),
        'shipping_type': fields.selection(
            [('postmail', 'PostMail CH: SmallSmall'),
             ('postlogistic', 'PostLogistics CH: Basic')],
            string='Shipping Type',
            required=True),
        'shipping_costs': fields.float(
            'Shipping Fees',
            required=True,
            digits_compute=dp.get_precision('Product Price')),
        'currency_id': fields.many2one(
            'res.currency',
            'Currency',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]},
            track_visibility='always'),
        #'sum_stock_available': fields.integer('Stock disponible', help='Stock reservé chez le fournisseur'),
        'sum_stock_available': fields.function(
            _get_stock,
            string='Available',
            type='integer',
            multi='stock'),
        'sum_stock_sold': fields.function(
            _get_stock,
            string='Sold and reserved',
            type='integer',
            multi='stock'),
        # XXX sum of stock of variants
        #'sum_stock_local': fields.integer('Stock local', help='Stock disponible'),
        'stock_progress': fields.function(
            _get_stock,
            string='Progress',
            type='float',
            multi='stock'),
        # XXX take product image ?
        'image': fields.binary(
            "Image",
            help="This field holds the image used as image for the product, "
                 "limited to 1024x1024px."),
        #'image_small': fields.function(_get_image, fnct_inv=_set_image,
            #string="Small-sized image", type="binary", multi="_get_image",
            #store={
                #'product.product': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            #},
            #help="Small-sized image of the product. It is automatically "\
                 #"resized as a 64x64px image, with aspect ratio preserved. "\
                 #"Use this field anywhere a small image is required."),
        'state': fields.selection(
            [('draft', 'Proposal'),
             ('open', 'Negociation'),
             ('planned', 'Planned'),
             ('done', 'Done'),
             ('cancel', 'Canceled')],
            'Status',
            readonly=True,
            required=True,
            track_visibility='onchange'),
        'company_id': fields.many2one(
            'res.company',
            string='Company',
            required=False,
            change_default=True,
            readonly=False,
            states={'done': [('readonly', True)]}),

        'date_warranty': fields.date(
            'Warranty Expiration',
            readonly=True,
            states={'draft': [('readonly', False)]}),

        # Indicators
        'shipping_max_delay': fields.integer(
            'Ship before (in days)',
            readonly=True,
            states={'draft': [('readonly', False)]},
            help="Maximum number of days before the delivery.\n"
                 "It can't be more than 10 days."),
    }

    def _default_company(self, cr, uid, context=None):
        company_obj = self.pool.get('res.company')
        return company_obj._company_default_get(cr, uid, 'qoqa.deal', context=context)

    _defaults = {
        'name': '/',
        'state': 'draft',
        'company_id': _default_company,
    }

    def _get_reference(self, cr, uid, context=None):
        """ Generate the reference based on a sequence """
        seq_obj = self.pool.get('ir.sequence')
        code = 'qoqa.deal'
        return seq_obj.get(cr, uid, code)

    def create(self, cr, uid, vals, context=None):
        if (vals.get('name', '/') or '/') == '/':
            vals['name'] = self._get_reference(cr, uid, context=context)
        return super(qoqa_deal, self).create(cr, uid, vals, context=context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default['name'] = '/'
        return super(qoqa_deal, self).copy_data(
            cr, uid, id, default=default, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def action_plan(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'planned'}, context=context)
        return True

    def onchange_product_tmpl_id(self, cr, uid, ids, product_tmpl_id,
                                 context=None):
        """
        Define the content of variant_ids depending on product_tmpl_id

        We will set automatically the variant if only one exists.

        If we replace a product by another, and if the new one has no variant,
        we try to keep the data of the stock data of first variant.

        Actually we erase everything if the template has many variants
        """
        res = {'value': {}}
        product_obj = self.pool.get('product.product')
        tmpl_variant_ids = product_obj.search(
            cr, uid,
            [('product_tmpl_id', '=', product_tmpl_id)],
            context=context)
        lines = [{'product_id': variant_id} for variant_id in tmpl_variant_ids]
        res['value']['variant_ids'] = lines
        return res

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for deal in self.browse(cr, uid, ids, context=context):
            name = deal.name + ' - ' + deal.product_tmpl_id.name
            res.append((deal.id, name))
        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            domain = ['|', ('name', operator, name),
                           ('product_tmpl_id.name', operator, name)]
            ids = self.search(cr, uid,
                              domain + args,
                              limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        result = self.name_get(cr, uid, ids, context=context)
        return result
