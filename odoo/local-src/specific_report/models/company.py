# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    number_empty_labels = fields.Integer(
        string='Number of empty labels between two batch pickings',
        default=8,
    )
