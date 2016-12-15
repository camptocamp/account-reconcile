# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    default_account_id = fields.Many2one(
        'account.account', 'Default account for product'
    )
