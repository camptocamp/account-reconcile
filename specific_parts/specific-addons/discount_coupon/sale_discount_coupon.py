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

import openerp.addons.decimal_precision as dp

from openerp.osv import orm, fields

class SaleDiscountCoupon(orm.Model):

    _name = 'sale.discount.coupon'
    _inherit = ['mail.thread']

    def _get_residual(self, cr, uid, ids, fields, args, context=None):
        res = dict.fromkeys(ids, 0)

        for coupon in self.browse(cr, uid, ids, context=context):
            res[coupon.id] = sum([line.price_subtotal for line in coupon.order_line_ids])

        return res

    _columns = {
        'name': fields.char('Numéro de Planning', required=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Type de bon', required=True, ondelete='cascade', domain=[('is_discount_coupon', '=', True)]),
        'date_begin': fields.datetime('Date début de validité', required=True),
        'date_end': fields.datetime('Date de fin de validité', required=True),
        'amount': fields.float('Montant du bon', required=True, digits_compute= dp.get_precision('Product Price')),
        'order_line_ids': fields.one2many('sale.order.line', 'coupon_id', 'Historique', readonly=True),
        'residual': fields.function(_get_residual, string='Solde', type='float'),
        }

    _defaults = {
        'name': '/',
        }

    def _get_reference(self, cr, uid, context=None):
        """
        Generate the reference based on sequence
        """
        if context is None:
            context = {}
        seq_obj = self.pool.get('ir.sequence')
        code = 'discount_coupon'
        return seq_obj.get(cr, uid, code)

    def create(self, cr, uid, values, context=None):

        ref = self._get_reference(cr, uid, context=context)
        values.update({'name': ref})

        return super(SaleDiscountCoupon, self).create(cr, uid, values, context=None)
