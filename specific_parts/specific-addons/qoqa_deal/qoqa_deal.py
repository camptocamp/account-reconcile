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
from datetime import datetime, timedelta
from openerp.tools import (DEFAULT_SERVER_DATETIME_FORMAT,
                           DEFAULT_SERVER_DATE_FORMAT)

import openerp.addons.decimal_precision as dp
from openerp.osv import orm, fields


class qoqa_deal(orm.Model):
    _name = 'qoqa.deal'
    _description = 'QoQa Deal'
    _inherit = ['mail.thread']

    _order = 'date_begin'

    DEAL_STATES = [('draft', 'Proposal'),
                   ('open', 'Negociation'),
                   ('planned', 'Planned'),
                   ('done', 'Done'),
                   ('cancel', 'Canceled'),
                   ]

    def _main_position_id(self, cr, uid, ids, fieldnames, args, context=None):
        position_obj = self.pool.get('qoqa.deal.position')
        res = {}
        for deal_id in ids:
            position_ids = position_obj.search(
                cr, uid,
                [('deal_id', '=', deal_id)],
                order='sequence asc',
                limit=1,
                context=context)
            try:
                res[deal_id] = position_ids[0]
            except IndexError:
                res[deal_id] = False
        return res

    def _full_dates(self, cr, uid, ids, fieldnames, args, context=None):
        date_fmt = DEFAULT_SERVER_DATE_FORMAT
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
        for deal in self.browse(cr, uid, ids, context=context):
            begin = datetime.strptime(deal.date_begin, date_fmt)
            begin += timedelta(hours=deal.time_begin)
            end = datetime.strptime(deal.date_end, date_fmt)
            end += timedelta(hours=deal.time_end)
            res[deal.id] = {
                'datetime_begin': begin.strftime(fmt),
                'datetime_end': end.strftime(fmt),
            }
        return res

    _columns = {
        'ref': fields.char('Deal Reference', required=True),
        'name': fields.char('Title', translate=True, required=True),
        'description': fields.html('Description', translate=True),
        'note': fields.html('Internal Notes', translate=True),
        'state': fields.selection(
            DEAL_STATES,
            'Status',
            readonly=True,
            required=True,
            track_visibility='onchange'),
        'qoqa_shop_id': fields.many2one(
            'qoqa.shop',
            string='Sell on',
            required=True),
        'position_ids': fields.one2many(
            'qoqa.deal.position',
            'deal_id',
            'Positions'),
        'main_position_id': fields.function(
            _main_position_id,
            string='Main Position',
            type='many2one',
            relation='qoqa.deal.position'),
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
        # date & time are split in 2 fields
        # because they should not be based on the UTC
        # if one says that a deal start on 2013-10-07 at 00:00
        # the QoQa backend expect to receive this date and time
        # without consideration of the UTC time
        'date_begin': fields.date(
            'Start Date',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'time_begin': fields.float(
            'Start Time',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'date_end': fields.date(
            'End Date',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]}),
        'time_end': fields.float(
            'End Time',
            required=True,
            readonly=True,
            states={'draft': [('readonly', False)]}),
        # for the display on the tree and kanban views
        'datetime_begin': fields.function(
            _full_dates,
            string='Begins at',
            type='char',
            multi='_full_dates',
            readonly=True),
        'datetime_end': fields.function(
            _full_dates,
            string='Ends at',
            type='char',
            multi='_full_dates',
            readonly=True),
        # for the group by day (group on date_begin gives a month group)
        'day': fields.related(
            'date_begin',
            type='char',
            string='Day',
            store=True),
        'shipper_service_id': fields.many2one(
            'delivery.service',
            string='Delivery Service'),
        'carrier_id': fields.many2one(
            'delivery.carrier',
            string='Shipping Method'),
        'pricelist_id': fields.many2one(
            'product.pricelist',
            string='Pricelist',
            required=True,
            domain="[('type', '=', 'sale')]",
            states={'draft': [('readonly', False)]}),
        'lang_id': fields.many2one(
            'res.lang',
            string='Language',
            states={'draft': [('readonly', False)]}),
        'company_id': fields.many2one(
            'res.company',
            string='Company',
            required=False,
            change_default=True,
            readonly=False,
            states={'done': [('readonly', True)]}),
        'qoqa_active': fields.boolean('Active on QoQa'),
        'date_warranty': fields.date(
            'Warranty Expiration',
            readonly=True,
            states={'draft': [('readonly', False)]}),
    }

    def _default_company(self, cr, uid, context=None):
        company_obj = self.pool.get('res.company')
        return company_obj._company_default_get(cr, uid, 'qoqa.deal', context=context)

    _defaults = {
        'ref': '/',
        'state': 'draft',
        'company_id': _default_company,
        'date_begin': fields.date.context_today,
        'date_end': fields.date.context_today,
        'time_begin': 0,  # 00:00
        'time_end': 23.983,  # 23:59
    }

    def _check_date(self, cr, uid, ids, context=None):
        date_fmt = DEFAULT_SERVER_DATE_FORMAT
        for deal in self.browse(cr, uid, ids, context=context):
            begin = datetime.strptime(deal.date_begin, date_fmt)
            begin += timedelta(hours=deal.time_begin)
            end = datetime.strptime(deal.date_end, date_fmt)
            end += timedelta(hours=deal.time_end)
            if begin > end:
                return False
        return True

    _constraints = [
        (_check_date, 'The beginning date must be anterior to the ending date',
         ['date_begin', 'date_end', 'time_begin', 'time_end']),
    ]

    def _get_reference(self, cr, uid, context=None):
        """ Generate the reference based on a sequence """
        seq_obj = self.pool.get('ir.sequence')
        return seq_obj.next_by_code(cr, uid, 'qoqa.deal')

    def create(self, cr, uid, vals, context=None):
        if (vals.get('ref', '/') or '/') == '/':
            vals['ref'] = self._get_reference(cr, uid, context=context)
        return super(qoqa_deal, self).create(cr, uid, vals, context=context)

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        else:
            default = default.copy()
        default['ref'] = '/'
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

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for deal in self.browse(cr, uid, ids, context=context):
            name = "[%s] %s" % (deal.ref, deal.name)
            res.append((deal.id, name))
        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            domain = ['|', ('ref', '=', name),
                           ('name', operator, name)]
            ids = self.search(cr, uid,
                              domain + args,
                              limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        result = self.name_get(cr, uid, ids, context=context)
        return result

    def onchange_date_begin(self, cr, uid, ids, date_begin, context=None):
        """ When changing the beginning date, automatically set the
        end date 24 hours later
        """
        if not date_begin:
            return {}
        return {'value': {'date_end': date_begin}}
