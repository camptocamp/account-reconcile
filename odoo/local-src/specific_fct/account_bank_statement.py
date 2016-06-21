# -*- coding: utf-8 -*-
# © 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.multi
    def button_journal_entries(self):
        # Remove existing groupbys
        # (to avoid non-existing fields on move lines)
        return super(AccountBankStatement, self).with_context(
            {k: v for k, v in self.env.context.items() if k != 'group_by'}
        ).button_journal_entries()
