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

from openerp.osv import orm, fields

class SaleOrderLine(orm.Model):

    _inherit = 'sale.order.line'

    _columns = {
        'coupon_id': fields.many2one('sale.discount.coupon', 'Discount Coupon', domain=[('residual', '>', 0)]),
        'so_date_order': fields.related('order_id', 'date_order', type='date', string='Date'),
        'so_partner_id': fields.related('order_id', 'partner_id', type='many2one', relation='res.partner', string='Customer'),
        'so_name': fields.related('order_id', 'name', type='char', string='Command number'),
        }
