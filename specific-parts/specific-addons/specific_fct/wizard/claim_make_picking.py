# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2016 Camptocamp SA
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
from openerp import netsvc


class claim_make_picking(orm.TransientModel):

    _inherit = 'claim_make_picking.wizard'

    def _get_source_loc(self, cr, uid, context):
        # Get destination for in, and set as source for out
        if context is None:
            context = {}
        if context.get('picking_type') != 'out' or \
                not context.get('partner_id'):
            return super(claim_make_picking, self)._get_source_loc(
                cr, uid, context=context)

        location_list = []
        # Retrieve used destination location in "IN"
        line_ids = self._get_claim_lines(cr, uid, context=context)
        for line in self.pool['claim.line'].browse(cr, uid, line_ids,
                                                   context=context):
            if line.move_in_id and line.move_in_id.location_dest_id:
                dest_location_id = line.move_in_id.location_dest_id.id
                if dest_location_id not in location_list:
                    location_list.append(dest_location_id)
        if len(location_list) == 1:
            return location_list[0]

        return super(claim_make_picking, self)._get_source_loc(
            cr, uid, context=context)

    _defaults = {
        'claim_line_source_location': _get_source_loc,
    }

    def _prepare_picking_vals(
            self, cr, uid, claim, p_type, partner_id, wizard, context=None,
            unclaimed_out=False):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        picking_vals = super(claim_make_picking, self)._prepare_picking_vals(
            cr, uid, claim, p_type, partner_id, wizard, context=context)
        if unclaimed_out and company.unclaimed_stock_journal_id:
            picking_vals.update({
                'stock_journal_id': company.unclaimed_stock_journal_id.id
            })
        return picking_vals

    """ copy whole method to remove check availability on picking """
    def action_create_picking(self, cr, uid, ids, context=None):
        picking_obj = self.pool['stock.picking']
        line_obj = self.pool['claim.line']
        claim_obj = self.pool['crm.claim']
        if context is None:
            context = {}
        view_obj = self.pool['ir.ui.view']
        name = 'RMA picking out'
        unclaimed_out = False
        if context.get('picking_type') == 'out':
            p_type = 'out'
            write_field = 'move_out_id'
        else:
            p_type = 'in'
            write_field = 'move_in_id'
            if context.get('picking_type'):
                name = 'RMA picking ' + str(context.get('picking_type'))
        model = 'stock.picking.' + p_type
        view_id = view_obj.search(cr, uid,
                                  [('model', '=', model),
                                   ('type', '=', 'form')],
                                  context=context)[0]
        wizard = self.browse(cr, uid, ids[0], context=context)
        claim = claim_obj.browse(cr, uid, context['active_id'],
                                 context=context)

        # Retrieve list of unclaimed categories
        unclaimed_categ_ids = []
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        company = user.company_id
        if company.unclaimed_initial_categ_id:
            unclaimed_categ_ids.append(
                company.unclaimed_initial_categ_id.id)
        if company.unclaimed_first_reminder_categ_id:
            unclaimed_categ_ids.append(
                company.unclaimed_first_reminder_categ_id.id)
        if company.unclaimed_second_reminder_categ_id:
            unclaimed_categ_ids.append(
                company.unclaimed_second_reminder_categ_id.id)

        # If claim has an unclaimed category, set the final one
        if (p_type == 'out' and
                claim.categ_id and
                claim.categ_id.id in unclaimed_categ_ids and
                company.unclaimed_final_categ_id):
            claim_obj.write(
                cr, uid, [claim.id],
                {'categ_id': company.unclaimed_final_categ_id.id},
                context=context
            )
            unclaimed_out = True

        partner_id = claim.delivery_address_id.id
        line_ids = [x.id for x in wizard.claim_line_ids]
        # In case of product return, we don't allow one picking for various
        # product if location are different
        # or if partner address is different
        if context.get('product_return'):
            common_dest_loc_id = self._get_common_dest_location_from_line(
                cr, uid, line_ids, context=context)
            if not common_dest_loc_id:
                raise orm.except_orm(
                    _('Error !'),
                    _('A product return cannot be created for various '
                      'destination locations, please choose line with a '
                      'same destination location.'))
            line_obj.auto_set_warranty(cr, uid, line_ids, context=context)
            common_dest_partner_id = self._get_common_partner_from_line(
                cr, uid, line_ids, context=context)
            if not common_dest_partner_id:
                raise orm.except_orm(
                    _('Error !'),
                    _('A product return cannot be created for various '
                      'destination addresses, please choose line with a '
                      'same address.'))
            partner_id = common_dest_partner_id
        # create picking
        picking_vals = self._prepare_picking_vals(
            cr, uid, claim, p_type, partner_id, wizard, context=context,
            unclaimed_out=unclaimed_out)
        picking_id = picking_obj.create(cr, uid, picking_vals, context=context)
        # Create picking lines
        proc_ids = []
        for wizard_line in wizard.claim_line_ids:
            if wizard_line.product_id.type not in ['consu', 'product']:
                continue
            move_id = self._create_move(
                cr, uid, wizard_line, partner_id, picking_id, wizard, claim,
                context=context)
            line_obj.write(
                cr, uid, wizard_line.id, {write_field: move_id},
                context=context)
            if p_type == 'out':
                proc_id = self._create_procurement(
                    cr, uid, wizard, claim, move_id, wizard_line,
                    context=context)
                proc_ids.append(proc_id)
        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking',
                                    picking_id, 'button_confirm', cr)
        if proc_ids:
            for proc_id in proc_ids:
                wf_service.trg_validate(uid, 'procurement.order',
                                        proc_id, 'button_confirm', cr)
        domain = ("[('type', '=', '%s'), ('partner_id', '=', %s)]" %
                  (p_type, partner_id))
        return {
            'name': '%s' % name,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'domain': domain,
            'res_model': model,
            'res_id': picking_id,
            'type': 'ir.actions.act_window',
        }
