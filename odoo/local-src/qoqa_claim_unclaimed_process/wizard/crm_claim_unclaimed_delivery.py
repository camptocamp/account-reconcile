# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import _, api, fields, models


class CrmClaimUnclaimedDelivery(models.TransientModel):
    _name = "crm.claim.unclaimed.delivery"

    claim_ids = fields.Many2many(
        relation='crm_claim_unclaimed_delivery_claim_ids_rel',
        comodel_name='crm.claim',
        string='Claims to be delivered',
        required=True
    )

    @api.multi
    def _create_unclaimed_invoice(self, claim):
        invoice_obj = self.env['account.invoice']
        # retrieve values
        company = self.env.user.company_id
        # Done because otherwise, the "main company" (QoQa Holding) is used
        # when reading properties from the product. Don't ask me why...
        company = company.with_context(force_company=company.id)
        analytic_account = self.env.ref(
            'scenario.analytic_account_shop_general_ch')
        inv_account = company.unclaimed_invoice_account_id
        inv_journal = company.unclaimed_invoice_journal_id
        product = company.unclaimed_invoice_product_id
        partner = claim.partner_id
        fiscal_position_id = partner.property_account_position_id and \
            partner.property_account_position_id.id or False
        payment_term_id = partner.property_payment_term_id and \
            partner.property_payment_term_id.id or False

        # Fill values (taken from on_change on invoice and invoice line)
        invoice_vals = {
            'account_id': inv_account.id,
            'company_id': company.id,
            'fiscal_position_id': fiscal_position_id,
            'journal_id': inv_journal.id,
            'partner_id': partner.id,
            'name': _('Refacturation Frais de renvoi'),
            'payment_term_id': payment_term_id,
            'reference': claim.code,
            'transaction_id': claim.code,
            'type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0,
                 {'account_analytic_id': analytic_account.id,
                  'account_id': product.property_account_income_id.id,
                  'invoice_line_tax_ids': [
                      (6, 0, [tax.id for tax in product.taxes_id])
                  ],
                  'name': product.partner_ref,
                  'product_id': product.id,
                  'price_unit': claim.unclaimed_price,
                  'uom_id': product.uom_id.id}
                 )
            ]
        }
        # create and open/validate invoice
        invoice = invoice_obj.create(invoice_vals)
        invoice.signal_workflow('invoice_open')

    @api.multi
    def deliver_claim(self):
        self.ensure_one()
        res_ids = []
        return_wiz_obj = self.env['claim_make_picking.wizard']
        act_window_obj = self.env['ir.actions.act_window']
        picking_obj = self.env['stock.picking']
        company = self.env.user.company_id
        picking_type = company.unclaimed_out_picking_type_id

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
                ('claim_id', '=', claim.id),
                ('picking_type_id', '=', picking_type.id)
            ]).ids
            # For unclaimed claims : create invoice
            if claim.unclaimed_price:
                self._create_unclaimed_invoice(claim)
        # Display created OUT pickings
        action = act_window_obj.for_xml_id('stock', 'action_picking_tree_all')
        invoice_domain = action.get('domain', False) and \
            eval(action['domain']) or []
        invoice_domain.append(('id', 'in', res_ids))
        action['domain'] = invoice_domain
        return action
