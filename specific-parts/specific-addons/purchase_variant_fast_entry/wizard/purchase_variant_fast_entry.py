# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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


class purchase_variant_fast_entry(orm.TransientModel):
    _name = 'purchase.variant.fast.entry'
    _description = 'Fast entry of variants in purchase orders'
    _columns = {
        'product_tmpl_id': fields.many2one('product.template',
                                           string='Product Template',
                                           required=True),
        'quantity': fields.float(
            'Default quantity',
            digits_compute=dp.get_precision('Product Unit of Measure')),
    }

    def _prepare_line(self, cr, uid, purchase, variant, quantity,
                      context=None):
        line = {
            'product_id': variant.id,
            'product_qty': quantity,
        }
        purchase_line_obj = self.pool['purchase.order.line']
        onchange = purchase_line_obj.onchange_product_id(
            cr, uid, [purchase.id], purchase.pricelist_id.id, variant.id,
            quantity, False, purchase.partner_id.id,
            date_order=purchase.date_order,
            fiscal_position_id=purchase.fiscal_position.id,
            date_planned=False, name=False, price_unit=False, context=context)
        line.update(onchange['value'])
        return line

    def fast_entry(self, cr, uid, ids, context=None):
        """ Create one purchase order line per variant of a product template
        """
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "Only 1 ID accepted, got %r" % ids
            ids = ids[0]
        if context is None:
            return
        form = self.browse(cr, uid, ids, context=context)
        purchase_ids = context.get('active_ids', [])
        purchase_obj = self.pool['purchase.order']
        purchases = purchase_obj.browse(cr, uid, purchase_ids, context=context)
        for purchase in purchases:
            lines = []
            for variant in form.product_tmpl_id.variant_ids:
                vals = self._prepare_line(cr, uid, purchase,
                                          variant, form.quantity,
                                          context=context)
                lines.append(vals)
            purchase.write({
                'order_line': [(0, 0, line) for line in lines],
            })
        return {'type': 'ir.actions.act_window_close'}
