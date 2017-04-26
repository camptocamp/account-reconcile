# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import models, fields


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    url = fields.Char(index=True)
