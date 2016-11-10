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
from openerp import api, fields, models
from openerp.addons.crm_claim_rma.wizards.claim_make_picking\
    import ClaimMakePicking as OldWizard


class ClaimMakePicking(models.TransientModel):
    _inherit = 'claim_make_picking.wizard'

    @api.model
    def _default_claim_line_source_location_id(self):
        super_wiz = super(ClaimMakePicking, self)
        # Get destination for in, and set as source for out
        if (self.env.context.get('picking_type') == 'out' and
                self.env.context.get('partner_id')):

            locations = self.env['stock.location'].browse()
            for line in self._default_claim_line_ids():
                locations |= line.move_in_id.location_dest_id
            if len(locations) == 1:
                return locations.id

        return super_wiz._default_claim_line_source_location_id()

    @api.model
    def _default_claim_line_dest_location_id(self):
        # Get destination for in, and set as source for out
        if (self.env.context.get('picking_type') == 'out' and
                self.env.context.get('partner_id')):

            locations = self.env['stock.location'].browse()
            for line in self._default_claim_line_ids():
                locations |= line.move_in_id.location_id
            if len(locations) == 1:
                return locations.id

        # For super(), use the class from crm_claim_rma directly (as the
        # method in crm_rma_stock_location does not use super, and warranty
        # information is not retrieved in that case)
        return OldWizard._default_claim_line_dest_location_id(self)

    claim_line_source_location_id = fields.Many2one(
        'stock.location', string='Source Location',
        default=_default_claim_line_source_location_id,
        help="Location where the returned products are from.")

    claim_line_dest_location_id = fields.Many2one(
        'stock.location', string='Dest. Location', required=True,
        default=_default_claim_line_dest_location_id,
        help="Location where the system will stock the returned products.")

    def _is_unclaimed(self, claim):
        # Retrieve list of unclaimed categories
        company = self.env.user.company_id
        unclaimed_categ_ids = [
            company.unclaimed_initial_categ_id.id,
            company.unclaimed_first_reminder_categ_id.id,
            company.unclaimed_second_reminder_categ_id.id,
            company.unclaimed_final_categ_id.id
        ]
        if claim.categ_id and claim.categ_id.id in unclaimed_categ_ids:
            return True
        return False

    def _get_picking_data(self, claim, picking_type, partner_id):
        company = self.env.user.company_id
        res = super(ClaimMakePicking, self)._get_picking_data(
            claim, picking_type, partner_id)
        if self._is_unclaimed(claim):
            if self.env.context.get('picking_type', False) == 'in':
                res['picking_type_id'] = \
                    company.unclaimed_in_picking_type_id.id
            else:
                res['picking_type_id'] = \
                    company.unclaimed_out_picking_type_id.id
        return res

    @api.multi
    def action_create_picking(self):
        # For QoQa, create an OUT picking instead of a procurement order
        if self.env.context.get('picking_type') != 'out':
            return super(ClaimMakePicking, self).action_create_picking()

        claim_obj = self.env['crm.claim']
        company = self.env.user.company_id
        claim = claim_obj.browse(self.env.context['active_id'])

        # If claim has an unclaimed category, set the final one
        if (self.env.context.get('picking_type', False) == 'out' and
                self._is_unclaimed(claim)):
            claim.write(
                {'categ_id': company.unclaimed_final_categ_id.id}
            )

        return self._create_picking(claim, 'out')
