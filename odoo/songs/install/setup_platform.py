# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem

from openerp.tools.config import config
from openerp.addons.cloud_platform.models.cloud_platform import FilestoreKind


@anthem.log
def main(ctx):
    """ Setup platform """
    CloudPlatform = ctx.env['cloud.platform']
    params = ctx.env['ir.config_parameter'].sudo()
    params.set_param('cloud.platform.kind', 'qoqa')
    environment = config['running_env']
    configs = CloudPlatform._config_by_server_env(environment)
    params.set_param('ir_attachment.location', configs.filestore)
    CloudPlatform.check()
    if configs.filestore == FilestoreKind.s3:
        ctx.env['ir.attachment'].sudo().force_storage()
