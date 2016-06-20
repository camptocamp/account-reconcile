# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import api, fields, models


class CrmClaimUnclaimedDelivery(models.TransientModel):
    _name = "crm.claim.unclaimed.delivery"

    claim_ids = fields.Many2many(
        relation='crm_claim_unclaimed_delivery_claim_ids_rel',
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
        picking_obj = self.env['stock.picking']

        for claim in self.claim_ids:
            # Call wizard for claim delivery
            ctx = {
                'active_id': claim.id,
                'warehouse_id': claim.warehouse_id.id,
                'partner_id': claim.partner_id.id,
                'picking_type': 'out',
            }
            return_wiz = return_wiz_obj.with_context(ctx).create({})
            # As "OUT" pickings are not directly returned, retrieve them from
            # the procurement group
            return_wiz.action_create_picking()
            res_ids += picking_obj.search([
                ('group_id.claim_id', '=', claim.id)
            ]).ids
        # Display created OUT pickings
        action = act_window_obj.for_xml_id('stock', 'action_picking_tree_all')
        invoice_domain = action.get('domain', False) and \
            eval(action['domain']) or []
        invoice_domain.append(('id', 'in', res_ids))
        action['domain'] = invoice_domain
        return action
