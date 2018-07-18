# -*- coding: utf-8 -*-

from openerp import fields, models


class BankStatementCamt(models.Model):
    _name = "account.bank.statement.camt"

    name = fields.Char(
        string='Text To Find',
        required=True,
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
    )
    memo_text = fields.Char(
        string="Memo Text",
        required=True,
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Text to find must be unique'),
    ]
