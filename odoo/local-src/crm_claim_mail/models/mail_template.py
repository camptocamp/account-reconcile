# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import fields, models


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    is_default = fields.Boolean()
