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

from openerp.osv import orm
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def action_force_cancel(self, cr, uid, ids, context=None):
        """ Force cancellation of a done sales order.

        Only usable on done sales orders (so in the final state of the
        workflow) to avoid to break the workflow in the middle of its
        course.
        At QoQa, they might deliver sales orders and only cancel the order
        afterwards. In that case, even if the sales order is done, they need
        to set it as canceled on OpenERP and on the backend.
        """
        sale_order_line_obj = self.pool.get('sale.order.line')
        for sale in self.browse(cr, uid, ids, context=context):
            if sale.state != 'done':
                raise orm.except_orm(
                    _('Cannot cancel this sales order!'),
                    _('Only done sales orders can be forced to be canceled.'))
            sale_order_line_obj.write(cr, uid,
                                      [l.id for l in sale.order_line],
                                      {'state': 'cancel'},
                                      context=context)
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        message = _("The sales order was done, but it has been manually "
                    "canceled.")
        self.message_post(cr, uid, ids, body=message, context=context)
        return True


class sale_order_line(orm.Model):

    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None):
        """ Does not copy the description in the line, keep only the name """

        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom, qty_uos=0,
            uos=uos, name=name, partner_id=partner_id, lang=lang,
            update_tax=update_tax, date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)

        if not product:
            return res

        pobj = self.pool['product.product']
        product_name = pobj.name_get(cr, uid, [product], context=context)[0][1]
        res['value']['name'] = product_name
        return res
