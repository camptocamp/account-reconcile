# -*- coding: utf-8 -*-
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    wine_exploitation_number = fields.Char('Wine exploitation number')
