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

class StockPicking(orm.Model):

    _inherit = 'stock.picking'

    _columns = {
        'deal_id': fields.many2one('sale.deal', 'Deal')
        }

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        invoice_vals = super(StockPicking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)

        invoice_vals.update(deal_id=picking.deal_id.id)
        return invoice_vals

class StockPickingOut(orm.Model):

    _inherit = 'stock.picking.out'

    _columns = {
        'deal_id': fields.many2one('sale.deal', 'Deal')
        }
