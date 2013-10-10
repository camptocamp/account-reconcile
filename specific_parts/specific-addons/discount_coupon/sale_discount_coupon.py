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

# XXX
"""
There are 4 types of coupon and different ways to create them
1. Bon cadeaux (acheté par une personne pour l’offrir à un tiers) / pas encore
We create a SO with a coupon. This must generate a coupon code.

2. Bon Rabais – rabais accordé par SAV à un client (Customer service)
This coupon is created by SAV no need to create a SO amount is debited on customer account

3. Bon Marketing – bons distribué lors d’events (Marketing / staff)
This is a code which can be used by multiple people but certainly only
once per SO this could be

Or is it a multiple unique codes ?

4. Bon Remboursement – remboursement de marchandise (pas encore)
This coupon is given as Bon Rabais
"""

class SaleDiscountCoupon(orm.Model):

    _name = 'sale.discount.coupon'
    _description = "Discount Coupon"
    _inherit = ['mail.thread']

    def _get_residual(self, cr, uid, ids, fields, args, context=None):
        res = dict.fromkeys(ids, 0)

        for coupon in self.browse(cr, uid, ids, context=context):
            res[coupon.id] = sum([line.price_subtotal for line in coupon.order_line_ids])

        return res

    def _get_coupon(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'name': fields.char('Code', required=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Coupon type', required=True, ondelete='cascade', domain=[('is_discount_coupon', '=', True)]),
        'date_begin': fields.date('Start of validity date', required=True),
        'date_end': fields.date('End of validity date', required=True),
        'amount': fields.float('Coupon amount', required=True, digits_compute= dp.get_precision('Product Price')),
        'order_line_ids': fields.one2many('sale.order.line', 'coupon_id', 'History', readonly=True),
        'residual': fields.function(_get_residual, string='Residual', type='float',
            store={
                'sale.discount': (lambda self, cr, uid, ids, c={}: ids, ['order_line_ids', 'amount'], 10),
                'sale.order.line': (_get_coupon, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            })
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
