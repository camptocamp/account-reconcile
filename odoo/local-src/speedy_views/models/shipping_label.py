# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import fields, models


class ShippingLabel(models.Model):
    _inherit = 'shipping.label'

    file_type = fields.Selection(index=True)
