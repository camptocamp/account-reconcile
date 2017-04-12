# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    partner_id = fields.Many2one(index=True)
    active = fields.Boolean(index=True)
