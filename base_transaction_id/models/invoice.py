# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    transaction_id = fields.Char(string='Transaction ID',
                                 index=True,
                                 copy=False,
                                 help="Transaction ID from the "
                                      "financial institute")

    @api.multi
    def action_move_create(self):
        """Propagate the transaction_id from the invoice to the move ref."""
        res = super().action_move_create()
        for invoice in self:
            if invoice.transaction_id:
                if invoice.move_id.ref:
                    # TODO add a test
                    invoice.move_id.ref += ' ' + invoice.transaction_id
                else:
                    invoice.move_id.ref = invoice.transaction_id
                # change the 'name' of the account move line on the total
                # balance line of the invoice. This is generally the last line
                # -> start from the end to find a line with the account set to
                # invoice.account_id
                for line in invoice.move_id.line_ids.sorted(reverse=True):
                    if line.account_id == invoice.account_id:
                        line.name = invoice.transaction_id
                        break
        return res
