# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models, api, SUPERUSER_ID
from .utils import install_trgm_extension, create_index


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    partner_id = fields.Many2one(index=True)
    claim_id = fields.Many2one(index=True)
    team_id = fields.Many2one(index=True)

    def init(self, cr):
        env = api.Environment(cr, SUPERUSER_ID, {})
        trgm_installed = install_trgm_extension(env)
        cr.commit()

        if trgm_installed:
            index_name = 'account_invoice_origin_gin_trgm'
            create_index(cr, index_name, self._table,
                         'USING gin (origin gin_trgm_ops)')

        # default list view sort by those fields desc
        index_name = 'account_invoice_list_sort_index'
        create_index(cr, index_name, self._table,
                     '(date_invoice desc, number desc, id desc) '
                     'WHERE active')

        # active is mostly used with 'true' so this partial index improves
        # globally the queries. The same index on (active) without where
        # would in general not be used.
        index_name = 'account_invoice_active_true_index'
        create_index(cr, index_name, self._table, '(active) where active')
