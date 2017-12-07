# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import fields, models, api, SUPERUSER_ID
from .utils import install_trgm_extension, create_index


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    url = fields.Char(index=True)

    def init(self, cr):
        env = api.Environment(cr, SUPERUSER_ID, {})
        trgm_installed = install_trgm_extension(env)
        cr.commit()

        if trgm_installed:
            index_name = 'ir_attachment_url_trgm_index'
            create_index(cr, index_name, self._table,
                         'USING gin (url gin_trgm_ops)')
