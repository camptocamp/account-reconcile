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

    @api.multi
    def button_validate_agreement(self):
        self.ensure_one()
        self.validation_agreement = True
