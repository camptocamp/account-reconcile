# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    ecotax = fields.Boolean('Ecotax')
