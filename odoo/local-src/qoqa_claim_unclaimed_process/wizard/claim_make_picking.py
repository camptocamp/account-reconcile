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

    @api.returns('res.partner')
    def _get_common_partner_from_line(self, lines):
        """ If all the lines have the same warranty return partner return that,
        else return an empty recordset. However, If the product return is to
        the company, and the chosen location has a partner, use this partner
        as the return address
        """
        dest_location = self.claim_line_dest_location_id
        dest_location_partner = dest_location.partner_id
        if dest_location_partner:
            warranties = lines.mapped('warranty_type')
            warranties = list(set(warranties))
            if len(warranties) == 1 and warranties[0] == 'company':
                return dest_location_partner

        partners = lines.mapped('warranty_return_partner')
        partners = list(set(partners))
        return partners[0] if len(partners) == 1 else self.env['res.partner']

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
        if claim.unclaimed_package_id:
            res['original_package_id'] = claim.unclaimed_package_id.id
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

    def _create_picking(self, claim, picking_type):
        # Add parameter to context to avoid action_assign for OUT pickings
        if picking_type == 'out':
            self = self.with_context(do_not_assign=True)
        return super(ClaimMakePicking, self)._create_picking(
            claim, picking_type)
