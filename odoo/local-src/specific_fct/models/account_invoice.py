# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountRefundDescription(models.Model):
    _name = 'account.refund.description'

    name = fields.Char('Description')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    validation_agreement = fields.Boolean('Agreement to validation')
    refund_description_id = fields.Many2one(
        'account.refund.description', 'Description', index=True,
        readonly=True, states={'draft': [('readonly', False)]}
    )

    @api.multi
    def action_move_create(self):
        # ensure that there is no analytic accounts on lines
        # when the policy is never
        lines = self.mapped('invoice_line_ids').filtered(
            lambda l: (
                l.account_id.user_type_id.analytic_policy == 'never' and
                l.account_analytic_id
            )
        )
        lines.write({'account_analytic_id': False})
        return super(AccountInvoice, self).action_move_create()

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if self.purchase_id and self.purchase_id.currency_id:
            self.currency_id = self.purchase_id.currency_id.id
        return super(AccountInvoice, self).purchase_order_change()

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        # Deactivate all currency change from the journal
        # (default or purchase currency is already set)
        return

    @api.onchange('reference')
    def _onchange_reference(self):
        # If name of the invoice is null we copy the value of reference
        if not self.name:
            self.name = self.reference

    @api.multi
    def button_validate_agreement(self):
        self.ensure_one()
        self.validation_agreement = True

    @api.multi
    @api.returns('self')
    def refund_with_description_id(
            self, date_invoice=None, date=None, description=None,
            journal_id=None, description_id=None):
        new_invoices = self.browse()
        for invoice in self:
            # create the new invoice
            values = self._prepare_refund(
                invoice, date_invoice=date_invoice, date=date,
                description=description, journal_id=journal_id)
            if description_id:
                values['refund_description_id'] = description_id
            new_invoices += self.create(values)
        return new_invoices
