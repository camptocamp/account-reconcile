# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def init(self, cr):
        cr.execute("""
            CREATE EXTENSION IF NOT EXISTS pg_trgm
        """)
        cr.commit()
        cr.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE indexname = 'account_invoice_origin_gin_trgm'
        """)
        if not cr.fetchone():
            cr.execute("""
                CREATE INDEX account_invoice_origin_gin_trgm
                ON account_invoice
                USING gin (origin gin_trgm_ops)
            """)
