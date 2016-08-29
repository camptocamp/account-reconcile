# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging
from openerp import api, fields, models
try:
    from openerp.addons.server_environment import serv_config
except ImportError:
    logging.getLogger('openerp.module').warning(
        'server_environment not available in addons path. '
        'server_env_connector_qoqa will not be usable')

_logger = logging.getLogger(__name__)


class QoqaBackend(models.Model):
    _inherit = 'qoqa.backend'

    @api.multi
    def _compute_server_env(self):
        for backend in self:
            for field_name in ('url', 'site_url', 'debug'):
                section_name = '.'.join((self._name.replace('.', '_'),
                                         backend.name))
                try:
                    value = serv_config.get(section_name, field_name)
                    setattr(backend, field_name,  value)
                except:
                    _logger.exception('error trying to read field %s '
                                      'in section %s', field_name,
                                      section_name)

    url = fields.Char(compute='_compute_server_env')
    site_url = fields.Char(compute='_compute_server_env')
    debug = fields.Boolean(compute='_compute_server_env')
