# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models
from .utils import create_index


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    partner_id = fields.Many2one(index=True)
    user_id = fields.Many2one(index=True)

    def init(self, cr):
        # active is mostly used with 'true' so this partial index improves
        # globally the queries. The same index on (active) without where
        # would in general not be used.
        index_name = 'crm_claim_active_true_index'
        create_index(cr, index_name, self._table, '(active) where active ')
