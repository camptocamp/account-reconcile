# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import models, fields


class MailAlias(models.Model):
    _inherit = "mail.alias"

    active = fields.Boolean(
        string='Active',
        default=True,
        help="The active field allows you to hide the record without "
             "removing it."
    )
