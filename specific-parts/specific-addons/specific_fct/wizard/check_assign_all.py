# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier, Matthieu Dietrich
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
from openerp.tools.translate import _


# define domain  for stock_picking_mass_assign,
# in order to use the new field from qoqa_offer,
# 'sale_create_date'
class check_assign_all(orm.TransientModel):
    _name = 'stock.picking.check.assign.all'
    _inherit = 'stock.picking.check.assign.all'
    _description = 'Delivery Orders Check Availability'

    def check(self, cr, uid, ids, context=None):
        context = context or {}
        picking_obj = self.pool['stock.picking']
        process_wizard_obj = self.pool['stock.partial.picking']
        picking_ids = context.get('active_ids')
        wizard_id = ids[0]

        if not picking_ids:
            raise orm.except_orm(
                _('Error'),
                _('No selected delivery orders'))

        wizard = self.browse(cr, uid, wizard_id, context=context)

        # Get confirmed pickings
        domain = [('type', '=', 'out'),
                  ('state', '=', 'confirmed'),
                  ('id', 'in', picking_ids)]
        confirmed_picking_ids = picking_obj.search(
            cr, uid, domain, order='sale_create_date', context=context)

        # Assign all picking if asked
        if wizard.check_availability and confirmed_picking_ids:
            picking_obj.check_assign_all(
                cr, uid, confirmed_picking_ids, context=context)

        # Force availability if asked
        if wizard.force_availability and confirmed_picking_ids:
            picking_obj.force_assign(cr, uid, confirmed_picking_ids)

        # Get all pickings ready to deliver
        domain = [('type', '=', 'out'),
                  ('state', '=', 'assigned'),
                  ('id', 'in', picking_ids)]
        assigned_picking_ids = picking_obj.search(
            cr, uid, domain, order='sale_create_date', context=context)

        # Cancal availability all pickings if asked
        if wizard.cancel_availability and assigned_picking_ids:
            picking_obj.cancel_assign(cr, uid, assigned_picking_ids)

        # Process all pickings if asked
        if wizard.process_picking and assigned_picking_ids:
            for picking in picking_obj.browse(
                    cr, uid, assigned_picking_ids, context=context):
                ctx = context.copy()
                ctx['active_ids'] = [picking.id]
                process_wizard_id = process_wizard_obj.create(
                    cr, uid, {}, context=ctx)
                process_wizard_obj.do_partial(
                    cr, uid, [process_wizard_id], context=context)

        # Get all pickings ready to invoice
        domain = [('type', '=', 'out'),
                  ('invoice_state', '=', '2binvoiced'),
                  ('id', 'in', picking_ids)]
        to_invoice_picking_ids = picking_obj.search(
            cr, uid, domain, order='sale_create_date', context=context)

        # Invoice all pickings if asked
        if wizard.create_invoice and to_invoice_picking_ids:
            # return the regular wizard to invoice many pickings
            ctx = context.copy()
            ctx['active_ids'] = to_invoice_picking_ids
            ctx['active_model'] = 'stock.picking.out'
            return {
                'name': _('Stock Invoice Onshipping'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.invoice.onshipping',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': ctx,
            }
        else:
            return True
