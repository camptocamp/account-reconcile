# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import fields, models


class QoqaTeam(models.Model):
    _name = "qoqa.team"

    name = fields.Char(
        string="Name",
        required=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help="The active field allows you to hide the picking without "
        "removing it."
    )
