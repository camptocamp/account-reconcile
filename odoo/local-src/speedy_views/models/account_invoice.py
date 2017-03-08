# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from openerp import models, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _trgm_extension_exists(self):
        self.env.cr.execute("""
            SELECT name, installed_version
            FROM pg_available_extensions
            WHERE name = 'pg_trgm'
            LIMIT 1;
            """)

        extension = self.env.cr.fetchone()
        if extension is None:
            return 'missing'

        if extension[1] is None:
            return 'uninstalled'

        return 'installed'

    @api.model
    def _is_postgres_superuser(self):
        self.env.cr.execute("SHOW is_superuser;")
        superuser = self.env.cr.fetchone()
        return superuser is not None and superuser[0] == 'on' or False

    @api.model
    def _install_trgm_extension(self):
        extension = self._trgm_extension_exists()
        if extension == 'missing':
            _logger.warning('To use pg_trgm you have to install the '
                            'postgres-contrib module.')
        elif extension == 'uninstalled':
            if self._is_postgres_superuser():
                self.env.cr.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
                return True
            else:
                _logger.warning('To use pg_trgm you have to create the '
                                'extension pg_trgm in your database or you '
                                'have to be the superuser.')
        else:
            return True
        return False

    def init(self, cr):
        installed = self._install_trgm_extension(cr, SUPERUSER_ID, context={})
        cr.commit()
        if installed:
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
