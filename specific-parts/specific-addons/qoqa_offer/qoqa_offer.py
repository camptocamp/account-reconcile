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
import math
from datetime import datetime, timedelta
import pytz
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT)
from openerp.tools.translate import _

from openerp.osv import orm, fields
import re


class qoqa_offer(orm.Model):
    _name = 'qoqa.offer'
    _description = 'QoQa Offer'
    _inherit = ['mail.thread']

    _order = 'date_begin'

    def _main_position_id(self, cr, uid, ids, fieldnames, args, context=None):
        position_obj = self.pool.get('qoqa.offer.position')
        res = {}
        for offer_id in ids:
            position_ids = position_obj.search(
                cr, uid,
                [('offer_id', '=', offer_id)],
                order='sequence asc',
                limit=1,
                context=context)
            try:
                res[offer_id] = position_ids[0]
            except IndexError:
                res[offer_id] = False
        return res

    def _full_dates(self, cr, uid, ids, fieldnames, args, context=None):
        """ Convert the dates for the display on the different views.

        Do not use the normal datetime fields to avoid timezone shifts.

        """
        date_fmt = DEFAULT_SERVER_DATE_FORMAT
        datetime_fmt = DEFAULT_SERVER_DATETIME_FORMAT
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        lang_obj = self.pool['res.lang']
        lang_ids = lang_obj.search(cr, uid,
                                   [('code', '=', user.lang)],
                                   context=context)
        dfmt = '%Y-%m-%d'
        tfmt = '%H:%M:%S'
        if lang_ids:
            lang = lang_obj.browse(cr, uid, lang_ids[0], context=context)
            if lang.date_format:
                dfmt = lang.date_format
            if lang.time_format:
                tfmt = lang.time_format
        fmt = dfmt + ' ' + tfmt
        res = {}
        for offer in self.browse(cr, uid, ids, context=context):
            begin = datetime.strptime(offer.date_begin, date_fmt)
            begin += timedelta(hours=offer.time_begin)
            end = datetime.strptime(offer.date_end, date_fmt)
            end += timedelta(hours=offer.time_end)

            # For filters we need a utc time
            local = pytz.timezone('Europe/Zurich')
            begin_local = local.localize(begin, is_dst=None)
            begin_utc = begin_local.astimezone(pytz.utc)
            end_local = local.localize(end, is_dst=None)
            end_utc = end_local.astimezone(pytz.utc)

            # Avoid to display an offer on number of calendar days + 1
            # when the last day is at midnight. Example:
            # Begin: 2013-12-04 00:00 End: 2013-12-05 00:00
            # We consider the last day to be 2013-12-04
            if offer.time_end == 0:
                calendar_end = end - timedelta(days=1)
            else:
                calendar_end = end

            res[offer.id] = {
                'datetime_begin': begin.strftime(fmt),
                'datetime_end': end.strftime(fmt),
                'datetime_begin_filter': begin_utc.strftime(datetime_fmt),
                'datetime_end_filter': end_utc.strftime(datetime_fmt),
                'date_begin_calendar': offer.date_begin,
                'date_end_calendar': calendar_end.strftime(datetime_fmt),
            }
        return res

    def _get_name(self, cr, uid, ids, fieldnames, args, context=None):
        """ Name of an offer is computed as:

        [Reference] + Brand of the main product + Name of the main product

        """
        res = {}
        empty = _('...?')
        for offer in self.browse(cr, uid, ids, context=context):
            if (not offer.main_position_id or
                    not offer.main_position_id.product_tmpl_id):
                res[offer.id] = {
                    'name': empty,
                    'main_brand': '',
                    'main_product_name': empty,
                }
                continue
            product_tmpl = offer.main_position_id.product_tmpl_id

            name = product_tmpl.name
            if product_tmpl.brand:
                brand = product_tmpl.brand
                name = "%s: %s" % (product_tmpl.brand, name)
            else:
                brand = False
            res[offer.id] = {
                'name': "[%s] %s" % (offer.ref, name),
                'main_brand': brand,
                'main_product_name': name,
            }
        return res

    def _get_stock(self, cr, uid, ids, fields, args, context=None):
        """Get stock numbers

        :returns: computed values
        :rtype: dict
        """
        res = {}
        for offer in self.browse(cr, uid, ids, context=context):
            quantity = 0
            residual = 0
            reserved = 0
            positions = offer.position_ids
            # if one of the position has an offline stock,
            # the global stock is maybe wrong so mark it as
            # 'offline'
            is_online = bool(positions and
                             all(pos.stock_is_online for pos in positions))
            online_failure = bool(positions and
                                  any(pos.stock_online_failure
                                      for pos in positions))
            for position in offer.position_ids:
                quantity += position.sum_quantity
                residual += position.sum_residual
                reserved += position.stock_reserved

            progress = 0.0
            if quantity > 0:
                progress = ((quantity - residual) / quantity) * 100

            reserved_percent = 0.0
            if quantity > 0:
                reserved_percent = reserved / quantity * 100

            progress_remaining = 100 - progress
            progress_bias = progress_remaining * offer.stock_bias / 100

            res[offer.id] = {
                'stock_is_online': is_online,
                'stock_online_failure': online_failure,
                'sum_quantity': quantity,
                'sum_residual': residual,
                'sum_stock_sold': quantity - residual,
                # always round up
                'stock_progress': math.ceil(progress),
                'stock_progress_remaining': progress_remaining,
                'stock_progress_with_bias': math.ceil(progress_bias),
                'stock_reserved': reserved,
                'stock_reserved_percent': math.ceil(reserved_percent),
            }
        return res

    def _get_offer_from_templates(self, cr, uid, ids, context=None):
        position_obj = self.pool.get('qoqa.offer.position')
        position_ids = position_obj.search(cr, uid,
                                           [('product_tmpl_id', 'in', ids)],
                                           context=context)
        offer_obj = self.pool.get('qoqa.offer')
        return offer_obj._get_offer_from_positions(
            cr, uid, position_ids, context=context)

    def _get_offer_from_positions(self, cr, uid, ids, context=None):
        position_obj = self.pool.get('qoqa.offer.position')
        positions = position_obj.read(cr, uid, ids,
                                      fields=['offer_id'],
                                      context=context)
        return [position['offer_id'][0] for position in positions]

    def _get_offer_from_sale_shop(self, cr, uid, ids, context=None):
        this = self.pool.get('qoqa.offer')
        offer_ids = this.search(cr, uid,
                                [('qoqa_shop_id.openerp_id', 'in', ids)],
                                context=context)
        return offer_ids

    _name_store = {
        _name: (lambda self, cr, uid, ids, c: ids,
                ['ref', 'position_ids'],
                10),
        'qoqa.offer.position': (_get_offer_from_positions,
                                ['product_tmpl_id'],
                                10),
        'product.template': (_get_offer_from_templates,
                             ['name', 'brand'],
                             10)
    }

    _columns = {
        'ref': fields.char('Offer Reference', required=True),
        'name': fields.function(
            _get_name,
            type='char',
            string='Ref and Name',
            readonly=True,
            multi='name',
            store=_name_store),
        'main_brand': fields.function(
            _get_name,
            type='char',
            string='Main Brand',
            readonly=True,
            multi='name',
            store=_name_store),
        'main_product_name': fields.function(
            _get_name,
            type='char',
            string='Main Product Name',
            readonly=True,
            multi='name',
            store=_name_store),
        'title': fields.char('Title', readonly=True, translate=True),
        'description': fields.html('Description',
                                   readonly=True,
                                   translate=True),
        'note': fields.html('Internal Notes'),
        'qoqa_shop_id': fields.many2one(
            'qoqa.shop',
            string='Sell on',
            required=True),
        'shop_kanban_image': fields.related(
            'qoqa_shop_id', 'kanban_image',
            string='Shop Image',
            type='binary',
            readonly=True),
        'position_ids': fields.one2many(
            'qoqa.offer.position',
            'offer_id',
            'Positions'),
        'main_position_id': fields.function(
            _main_position_id,
            string='Main Position',
            type='many2one',
            relation='qoqa.offer.position'),
        'image_small': fields.related(
            'main_position_id', 'image_small',
            string='Thumbnail',
            type='binary',
            readonly=True),
        'image_medium': fields.related(
            'main_position_id', 'image_medium',
            string='Medium-sized Image',
            type='binary',
            readonly=True),
        'stock_progress': fields.related(
            'main_position_id', 'stock_progress',
            string='Progress',
            type='float',
            readonly=True),
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
        'sum_quantity': fields.function(
            _get_stock,
            string='Quantity',
            type='integer',
            multi='stock'),
        'sum_residual': fields.function(
            _get_stock,
            string='Residual',
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
            type='integer',
            multi='stock'),
        'stock_progress_with_bias': fields.function(
            _get_stock,
            string='Remaining with Bias (%)',
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
        # date & time are split in 2 fields
        # because they should not be based on the UTC
        # if one says that a offer start on 2013-10-07 at 00:00
        # the QoQa backend expect to receive this date and time
        # without consideration of the UTC time
        'date_begin': fields.date(
            'Start Date',
            required=True),
        'time_begin': fields.float(
            'Start Time',
            required=True),
        'date_end': fields.date(
            'End Date',
            required=True),
        'time_end': fields.float(
            'End Time',
            required=True),
        # for the display on the tree and kanban views
        'datetime_begin': fields.function(
            _full_dates,
            string='Begins at',
            type='char',
            multi='_full_dates',
            store=True,
            readonly=True),
        'datetime_end': fields.function(
            _full_dates,
            string='Ends at',
            type='char',
            multi='_full_dates',
            store=True,
            readonly=True),
        # used in search view 'current' filter
        # a datetime is necessary instead of a char
        'datetime_begin_filter': fields.function(
            _full_dates,
            string='Begins at',
            type='datetime',
            multi='_full_dates',
            store=True,
            readonly=True),
        'datetime_end_filter': fields.function(
            _full_dates,
            string='Ends at',
            type='datetime',
            multi='_full_dates',
            store=True,
            readonly=True),
        # display on the calendar
        # use a date and not a datetime to avoid timezone shifts
        'date_begin_calendar': fields.function(
            _full_dates,
            string='Begins at (Calendar)',
            type='date',
            multi='_full_dates',
            store=True,
            readonly=True),
        'date_end_calendar': fields.function(
            _full_dates,
            string='Ends at (Calendar)',
            type='date',
            multi='_full_dates',
            readonly=True,
            store=True,
            help="When an ending date is date_begin + 1 day at 00:00 "
                 "this date is set at date_begin, so the calendar won't "
                 "display the offer on 2 days"),
        # for the group by day (group on date_begin gives a month group)
        'day': fields.related(
            'date_begin',
            type='char',
            string='Day',
            store=True),
        'carrier_id': fields.many2one(
            'delivery.carrier',
            string='Delivery Method',
            domain="[('qoqa_type', '=', 'service')]"),
        'shipper_rate_id': fields.many2one(
            'delivery.carrier',
            string='Shipper Rate',
            required=True,
            domain="[('qoqa_type', '=', 'rate')]"),
        'pricelist_id': fields.many2one(
            'product.pricelist',
            string='Pricelist',
            domain="[('type', '=', 'sale')]",
            required=True),
        'lang_id': fields.many2one(
            'res.lang',
            string='Language',
            domain=[('translatable', '=', True)]),
        'company_id': fields.related(
            'qoqa_shop_id', 'company_id',
            string='Company',
            type='many2one',
            relation='res.company',
            readonly=True,
            store={
                _name: (lambda self, cr, uid, ids, c: ids,
                        ['qoqa_shop_id'], 10),
                'sale.shop': (_get_offer_from_sale_shop, ['company_id'], 10),
            }),
        'date_warranty': fields.date(
            'Warranty Expiration',
            readonly=True),
        'send_newsletters': fields.boolean('Send newsletters'),
        'active': fields.boolean('Active'),
        'sale_ids': fields.one2many(
            'sale.order', 'offer_id',
            string='Sales Orders'),
        # related to main position for kanban view:
        'currency_symbol': fields.related(
            'pricelist_id', 'currency_id', 'symbol',
            type='char', string='Currency', readonly=True),
        'main_lot_price': fields.related(
            'main_position_id', 'lot_price',
            string='Unit Price', type='float',
            readonly=True),
        'main_regular_price': fields.related(
            'main_position_id', 'regular_price',
            string='Unit Price', type='float', readonly=True),
        'stock_bias': fields.integer('Stock Bias'),
    }

    def _default_date_end(self, cr, uid, context=None):
        date_fmt = DEFAULT_SERVER_DATE_FORMAT
        today = fields.date.context_today(self, cr, uid, context=context)
        today = datetime.strptime(today, date_fmt)
        return (today + timedelta(days=1)).strftime(date_fmt)

    _defaults = {
        'stock_bias': 100,
        'ref': '/',
        'date_begin': fields.date.context_today,
        'date_end': _default_date_end,
        'time_begin': 0,  # 00:00'
        'time_end': 0,
        'send_newsletters': 1,
        'active': 1,
    }

    def _check_date(self, cr, uid, ids, context=None):
        date_fmt = DEFAULT_SERVER_DATE_FORMAT
        for offer in self.browse(cr, uid, ids, context=context):
            begin = datetime.strptime(offer.date_begin, date_fmt)
            begin += timedelta(hours=offer.time_begin)
            end = datetime.strptime(offer.date_end, date_fmt)
            end += timedelta(hours=offer.time_end)
            if begin > end:
                return False
        return True

    def _check_pricelist_company(self, cr, uid, ids, context=None):
        for offer in self.browse(cr, uid, ids, context=context):
            if not offer.pricelist_id:
                continue
            if offer.qoqa_shop_id.company_id != offer.pricelist_id.company_id:
                return False
        return True

    _constraints = [
        (_check_date, 'The beginning date must be anterior to the ending date',
         ['date_begin', 'date_end', 'time_begin', 'time_end']),
        (_check_pricelist_company,
         'The pricelist and the shop must belong to the same company.',
         ['pricelist_id', 'qoqa_shop_id']),
    ]

    def _get_reference(self, cr, uid, context=None):
        """ Generate the reference based on a sequence """
        seq_obj = self.pool.get('ir.sequence')
        return seq_obj.next_by_code(cr, uid, 'qoqa.offer')

    def _clean_html_description(self, vals):
        """ In Chrome, editing the description in cleditor
            puts <div> instead of <p>; not much we can do but
            clean up the stored value."""
        if 'description' in vals and vals['description']:
            vals['description'] = re.sub(r'<(\/?)div>', r'<\1p>',
                                         vals['description'])

    def create(self, cr, uid, vals, context=None):
        if (vals.get('ref', '/') or '/') == '/':
            vals['ref'] = self._get_reference(cr, uid, context=context)
        # Clean the content of the description
        self._clean_html_description(vals)
        return super(qoqa_offer, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        # Clean the content of the description
        self._clean_html_description(vals)
        return super(qoqa_offer, self).write(cr, uid, ids, vals,
                                             context=context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default.setdefault('ref', '/')
        default.setdefault('sale_ids', False)
        return super(qoqa_offer, self).copy_data(
            cr, uid, id, default=default, context=context)

    def onchange_date_begin(self, cr, uid, ids, date_begin, context=None):
        """ When changing the beginning date, automatically set the
        end date 24 hours later
        """
        if not date_begin:
            return {}
        return {'value': {'date_end': date_begin}}

    def action_view_sale_order(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        action_xmlid = ('sale', 'action_orders')
        ref = mod_obj.get_object_reference(cr, uid, *action_xmlid)
        action_id = False
        if ref:
            __, action_id = ref
        action = act_obj.read(cr, uid, [action_id], context=context)[0]
        action['domain'] = str([('offer_id', 'in', ids)])
        return action

    def decrement_stock_bias(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        for offer in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, offer.id,
                       {'stock_bias': offer.stock_bias - 1},
                       context=context)
        return True

    def button_orderpoint(self, cr, uid, ids, context=None):
        products = set()
        for offer in self.browse(cr, uid, ids, context=context):
            for position in offer.position_ids:
                for variant in position.variant_ids:
                    products.add(variant.product_id)
        orderpoint_ids = set()
        for product in products:
            for orderpoint in product.orderpoint_ids:
                orderpoint_ids.add(orderpoint.id)
        if not orderpoint_ids:
            raise orm.except_orm(
                _('Error'),
                _('The products have no orderpoints configured.')
            )
        orderpoint_obj = self.pool['stock.warehouse.orderpoint']
        procurement_obj = self.pool['procurement.order']
        orderpoint_confirm = orderpoint_obj.procure_orderpoint_confirm
        procurement_ids = orderpoint_confirm(cr, uid, list(orderpoint_ids),
                                             context=context)
        purchase_ids = []
        procurements = procurement_obj.browse(cr, uid, procurement_ids,
                                              context=context)
        for procurement in procurements:
            if procurement.purchase_id:
                purchase_ids.append(procurement.purchase_id.id)
        return {
            'domain': "[('id', 'in', %s)]" % purchase_ids,
            'name': _('Generated Purchases'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
