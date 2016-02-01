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


class CrmClaimUnclaimedDelivery(orm.TransientModel):
    _name = "crm.claim.unclaimed.delivery"

    _columns = {
        'claim_ids': fields.many2many(
            'crm.claim',
            'crm_claim_unclaimed_delivery_rel',
            'wizard_id', 'claim_id',
            'Claims to be delivered',
            required=True)
    }

    def deliver_claim(self, cr, uid, ids, context=None):
        res_ids = []
        claim_obj = self.pool['crm.claim']
        return_wiz_obj = self.pool['claim_make_picking.wizard']
        wizard = self.browse(cr, uid, ids[0], context=context)

        claim_ids = [claim.id for claim in wizard.claim_ids]
        for claim in claim_obj.browse(cr, uid, claim_ids, context=context):
            # Call wizard for claim delivery
            ctx = {
                'active_id': claim.id,
                'warehouse_id': claim.warehouse_id.id,
                'partner_id': claim.partner_id.id,
                'picking_type': 'out',
            }
            return_wiz_id = return_wiz_obj.create(cr, uid, {}, context=ctx)
            wiz_result = return_wiz_obj.action_create_picking(
                cr, uid, [return_wiz_id], context=ctx)
            if 'res_id' in wiz_result:
                res_ids.append(wiz_result['res_id'])
        # Display created OUT pickings
        _, act_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'stock', 'action_picking_tree')
        act_window = self.pool['ir.actions.act_window'].read(
            cr, uid, act_id, context=context)
        invoice_domain = eval(act_window['domain'])
        invoice_domain.append(('id', 'in', res_ids))
        act_window['domain'] = invoice_domain
        return act_window
