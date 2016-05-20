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

from openerp.osv import orm, fields


class sale_order(orm.Model):

    _inherit = 'sale.order'

    _columns = {
        # Override transaction_id to add an index
        # to optimize a query. Could consider adding the index
        # in base_transaction_id but I could not find from
        # where the query was issued
        'transaction_id': fields.char(
            'Transaction id',
            size=128,
            required=False,
            select=True,
            help="Transaction id from the financial institute"),
    }


class sale_order_line(orm.Model):

    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
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
