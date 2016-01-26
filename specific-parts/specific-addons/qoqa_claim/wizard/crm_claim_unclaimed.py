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
from openerp.osv import orm, fields
from openerp import netsvc


class CrmClaimUnclaimed(orm.TransientModel):
    _name = 'crm.claim.unclaimed'

    def _default_section_id(self, cr, uid, context=None):
        _, section_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'scenario', 'section_sale_team_livr')
        return section_id

    def _default_user_id(self, cr, uid, context=None):
        section_id = self._default_section_id(cr, uid, context=context)
        section = self.pool['crm.case.section'].browse(cr, uid, section_id,
                                                       context=context)
        return section.user_id and section.user_id.id or False

    def _default_company_id(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.id or False

    def _default_categ_id(self, cr, uid, context=None):
        company_id = self._default_company_id(cr, uid, context=context)
        company = self.pool['res.company'].browse(cr, uid, company_id,
                                                  context=context)
        return company.unclaimed_category_id and \
            company.unclaimed_category_id.id or False

    _columns = {
        'track_number': fields.char(
            'Tracking Number', size=32, required=True),
        'claim_name': fields.char(
            'Claim Subject', size=128, required=True),
        'return_source_location_id': fields.many2one(
            'stock.location', 'Source Location', required=True),
        'return_dest_location_id': fields.many2one(
            'stock.location', 'Dest. Location', required=True),
        'claim_invoice_id': fields.many2one(
            'account.invoice', 'Invoice', required=True),
        'claim_sale_order_id': fields.many2one(
            'sale.order', 'Sale Order', required=True),
        'claim_partner_id': fields.many2one(
            'res.partner', 'Customer', required=True),
        'claim_user_id': fields.many2one(
            'res.users', 'Responsible', required=True),
        'claim_section_id': fields.many2one(
            'crm.case.section', 'Sales Team', required=True),
        'claim_categ_id': fields.many2one(
            'crm.case.categ', 'Category', required=True),
        'claim_company_id': fields.many2one(
            'res.company', 'Company', required=True),
    }

    _defaults = {
        'claim_section_id': _default_section_id,
        'claim_user_id': _default_user_id,
        'claim_company_id': _default_company_id,
        'claim_categ_id': _default_categ_id,
    }

    def onchange_package_number(self, cr, uid, ids,
                                track_number, context=None):
        res = {'value': {'claim_name': False,
                         'return_dest_location_id': False,
                         'claim_invoice_id': False,
                         'claim_sale_order_id': False,
                         'claim_partner_id': False}}
        track_obj = self.pool['stock.tracking']
        if not track_number:
            return res

        res['value'].update({
            'claim_name': 'Unclaimed return of package %s' % track_number
        })
        track_ids = track_obj.search(
            cr, uid, [('serial', '=', track_number)], context=context)
        if not track_ids:
            return res

        track = track_obj.browse(cr, uid, track_ids[0], context=context)
        move = track.move_ids and track.move_ids[0] or False
        if not move:
            return
        res['value'].update({
            'return_source_location_id': move.location_dest_id.id,
            'return_dest_location_id': move.location_id.id
        })
        sale = move.sale_line_id and move.sale_line_id.order_id or False
        if not sale:
            return
        invoice = sale.invoice_ids and sale.invoice_ids[0] or False
        res['value'].update({
            'claim_invoice_id': invoice.id,
            'claim_sale_order_id': sale.id,
            'claim_partner_id': sale.partner_id.id
        })
        return res

    def create_claim(self, cr, uid, ids, context=None):
        # Function to create claim and return with given parameters
        claim_obj = self.pool['crm.claim']
        return_wiz_obj = self.pool['claim_make_picking.wizard']
        wizard = self.browse(cr, uid, ids[0], context=context)
        claim_vals = {
            'name': wizard.claim_name,
            'user_id': wizard.claim_user_id.id,
            'section_id': wizard.claim_section_id.id,
            'claim_type': 'customer',
            'categ_id': wizard.claim_categ_id.id,
            'ref': 'sale.order,%s' % wizard.claim_sale_order_id.id,
            'partner_id': wizard.claim_partner_id.id,
            'invoice_id': wizard.claim_invoice_id.id,
            'company_id': wizard.claim_company_id.id
        }
        on_change_partner_vals = claim_obj.onchange_partner_id(
            cr, uid, [], wizard.claim_partner_id.id)
        claim_vals.update(on_change_partner_vals['value'])

        on_change_invoice_vals = claim_obj.onchange_invoice_id(
            cr, uid, ids, invoice_id=wizard.claim_invoice_id.id,
            warehouse_id=False, claim_type='customer',
            claim_date=fields.datetime.now(),
            company_id=wizard.claim_company_id.id,
            lines=False, create_lines=True, context=context)
        claim_vals.update(on_change_invoice_vals['value'])
        # store correctly claim lines
        if 'claim_line_ids' in claim_vals:
            claim_vals['claim_line_ids'] = \
                [(0, 0, line) for line in claim_vals['claim_line_ids']]

        # Create and resolve claim
        print claim_vals
        claim_id = claim_obj.create(cr, uid, claim_vals, context=context)
        claim_obj.case_close(cr, uid, [claim_id], context=context)

        # Create refund from claim
        claim = claim_obj.browse(cr, uid, claim_id, context=context)
        ctx = context.copy()
        ctx.update({'active_id': claim_id,
                    'warehouse_id': claim.warehouse_id.id,
                    'partner_id': claim.partner_id.id,
                    'picking_type': 'in',
                    'product_return': True})
        return_wiz_id = return_wiz_obj.create(
            cr, uid, {
                'claim_line_source_location': wizard.return_source_location_id.id,
                'claim_line_dest_location': wizard.return_dest_location_id.id
            }, context=ctx
        )
        wiz_result = return_wiz_obj.action_create_picking(
            cr, uid, [return_wiz_id], context=ctx)
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'stock.picking',
                                wiz_result['res_id'],
                                'button_done', cr)
        return wiz_result

