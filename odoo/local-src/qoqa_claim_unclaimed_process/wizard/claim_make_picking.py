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
from openerp import _, api, models


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

    @api.multi
    def _create_unclaimed_invoice(self, claim):
        invoice_obj = self.env['account.invoice']
        # retrieve values
        company = self.env.user.company_id
        analytic_account = self.env.ref(
            'scenario.analytic_account_shop_general_ch')
        inv_account = company.unclaimed_invoice_account_id
        inv_journal = company.unclaimed_invoice_journal_id
        product = company.unclaimed_invoice_product_id
        partner = claim.partner_id
        fiscal_position = partner.property_account_position and \
            partner.property_account_position.id or False
        payment_term = partner.property_payment_term and \
            partner.property_payment_term.id or False

        # Fill values (taken from on_change on invoice and invoice line)
        invoice_vals = {
            'account_id': inv_account.id,
            'company_id': company.id,
            'fiscal_position': fiscal_position,
            'journal_id': inv_journal.id,
            'partner_id': partner.id,
            'name': _('Refacturation Frais de renvoi'),
            'payment_term': payment_term,
            'reference': claim.code,
            'transaction_id': claim.code,
            'type': 'out_invoice',
            'invoice_line': [
                (0, 0,
                 {'account_analytic_id': analytic_account.id,
                  'account_id': product.property_account_income.id,
                  'invoice_line_tax_id': [
                      (6, 0, [tax.id for tax in product.taxes_id])
                  ],
                  'name': product.partner_ref,
                  'product_id': product.id,
                  'price_unit': claim.unclaimed_price,
                  'uos_id': product.uom_id.id}
                 )
            ]
        }
        # create and open/validate invoice
        invoice = invoice_obj.create(invoice_vals)
        invoice.signal_workflow('invoice_open')

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
            if claim.unclaimed_price:
                self._create_unclaimed_invoice(claim)

        return super(ClaimMakePicking, self).action_create_picking()
