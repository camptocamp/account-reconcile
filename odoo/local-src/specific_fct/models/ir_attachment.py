# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os
import logging
from contextlib import closing

import openerp
from openerp import api, models

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def migrate_small_attachments_from_s3_to_db(self):
        """ Migrate some attachments from S3 back to database

        The access to a file stored on the objects storage is slower
        than a local disk or database access. For attachments like
        image_small that are accessed in batch for kanban views, this
        is too slow. We store this type of attachment in the database.

        This method will only be used once during the migration to Odoo 9.0

        It is copied from a migration of the 'attachment_s3' module.
        """
        cr = self.env.cr
        cr.execute("""
            SELECT value FROM ir_config_parameter
            WHERE key = 'ir_attachment.location'
        """)
        row = cr.fetchone()
        bucket = os.environ.get('AWS_BUCKETNAME')

        if row[0] == 's3' and bucket:
            uid = openerp.SUPERUSER_ID
            registry = openerp.modules.registry.RegistryManager.get(cr.dbname)
            new_cr = registry.cursor()
            with closing(new_cr):
                with openerp.api.Environment.manage():
                    env = openerp.api.Environment(new_cr, uid, {})
                    store_local = env['ir.attachment'].search(
                        [('store_fname', '=like', 's3://%'),
                         '|', ('res_model', '=', 'ir.ui.view'),
                              ('res_field', 'in', ['image_small',
                                                   'image_medium',
                                                   'web_icon_data'])
                         ],
                    )

                    _logger.info(
                        'Moving %d attachments from S3 to DB for fast access',
                        len(store_local)
                    )
                    for attachment_id in store_local.ids:
                        # force re-storing the document, will move
                        # it from the object storage to the database

                        # This is a trick to avoid having the 'datas' function
                        # fields computed for every attachment on each
                        # iteration of the loop.  The former issue being that
                        # it reads the content of the file of ALL the
                        # attachments on each loop.
                        try:
                            env.clear()
                            attachment = env['ir.attachment'].browse(
                                attachment_id
                            )
                            _logger.info('Moving attachment %s (id: %s)',
                                         attachment.name, attachment.id)
                            attachment.write({'datas': attachment.datas})
                            new_cr.commit()
                        except Exception:
                            new_cr.rollback()
