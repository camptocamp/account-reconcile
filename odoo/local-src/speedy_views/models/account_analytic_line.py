# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    so_line = fields.Many2one(index=True)
