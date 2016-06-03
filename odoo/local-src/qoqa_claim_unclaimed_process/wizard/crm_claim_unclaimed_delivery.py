# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import api, fields, models


class CrmClaimUnclaimedDelivery(models.TransientModel):
    _name = "crm.claim.unclaimed.delivery"

    claim_ids = fields.Many2many(
        relation='crm_claim_unclaimed_delivery_rel',
        comodel_name='crm.claim',
        string='Claims to be delivered',
        required=True
    )

    @api.multi
    def deliver_claim(self):
        self.ensure_one()
        res_ids = []
        return_wiz_obj = self.env['claim_make_picking.wizard']
        act_window_obj = self.env['ir.actions.act_window']

        for claim in self.claim_ids:
            # Call wizard for claim delivery
            ctx = {
                'active_id': claim.id,
                'warehouse_id': claim.warehouse_id.id,
                'partner_id': claim.partner_id.id,
                'picking_type': 'out',
            }
            return_wiz = return_wiz_obj.with_context(ctx).create({})
            wiz_result = return_wiz.action_create_picking()
            if 'res_id' in wiz_result:
                res_ids.append(wiz_result['res_id'])
        # Display created OUT pickings
        action = act_window_obj.for_xml_id('stock', 'action_picking_tree')
        invoice_domain = eval(action['domain'])
        invoice_domain.append(('id', 'in', res_ids))
        action['domain'] = invoice_domain
        return action
