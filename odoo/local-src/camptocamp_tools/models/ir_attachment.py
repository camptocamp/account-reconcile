# -*- coding: utf-8 -*-
# This file has been generated with 'invoke project.sync'.
# Do not modify. Any manual change will be lost.
# Please propose your modification on
# https://github.com/camptocamp/odoo-template instead.
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, api, SUPERUSER_ID
from ..utils import install_trgm_extension, create_index


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_cr
    def init(self):
        """ Add index on ir_attachment.url to speed up the initial request
            made each time a page is (re)loaded :
            `select id from ir_attachment where url like '/web/content%'`
        """
        env = api.Environment(self._cr, SUPERUSER_ID, {})
        trgm_installed = install_trgm_extension(env)
        self._cr.commit()

        if trgm_installed:
            index_name = 'ir_attachment_url_trgm_index'
            create_index(self._cr, index_name, self._table,
                         'USING gin (url gin_trgm_ops)')
