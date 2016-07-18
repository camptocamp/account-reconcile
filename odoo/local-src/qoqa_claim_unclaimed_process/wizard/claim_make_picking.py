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
from openerp import api, models


class ClaimMakePicking(models.TransientModel):
    _inherit = 'claim_make_picking.wizard'

    @api.model
    def _default_claim_line_source_location_id(self):
        super_wiz = super(ClaimMakePicking, self)
        # Get destination for in, and set as source for out
        if (self.env.context.get('picking_type') == 'out' and
                self.context.get('partner_id')):

            location_list = []
            # Retrieve used destination location in "IN"
            lines = self._default_claim_line_ids()
            for line in lines:
                if line.move_in_id and line.move_in_id.location_dest_id:
                    dest_location_id = line.move_in_id.location_dest_id.id
                    if dest_location_id not in location_list:
                        location_list.append(dest_location_id)
            if len(location_list) == 1:
                return location_list[0]

        return super_wiz._default_claim_line_source_location_id()

    """ copy whole method to remove check availability on picking """
    @api.multi
    def action_create_picking(self):
        claim_obj = self.env['crm.claim']
        claim = claim_obj.browse(self.env.context['active_id'])

        # Retrieve list of unclaimed categories
        company = self.env.user.company_id
        unclaimed_categ_ids = [
            company.unclaimed_initial_categ_id.id,
            company.unclaimed_first_reminder_categ_id.id,
            company.unclaimed_second_reminder_categ_id.id
        ]

        # If claim has an unclaimed category, set the final one
        if (self.env.context.get('picking_type', False) == 'out' and
                claim.categ_id and
                claim.categ_id.id in unclaimed_categ_ids and
                company.unclaimed_final_categ_id):
            claim.write(
                {'categ_id': company.unclaimed_final_categ_id.id}
            )

        return super(ClaimMakePicking, self).action_create_picking()
