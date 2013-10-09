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


class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'offer_id': fields.many2one(
            'qoqa.offer',
            string='Offer',
            readonly=True,
            ondelete='restrict')
    }

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        vals = super(sale_order, self)._prepare_invoice(
            cr, uid, order, lines, context=context)
        if order.offer_id:
            vals['offer_id'] = order.offer_id.id
        return vals

    def _prepare_order_picking(self, cr, uid, order, context=None):
        vals = super(sale_order, self)._prepare_order_picking(
            cr, uid, order, context=context)
        if order.offer_id:
            vals['offer_id'] = order.offer_id.id
        return vals
