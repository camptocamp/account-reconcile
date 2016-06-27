# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import os
import base64
from boto.s3.connection import S3Connection
from openerp import api, fields, models
try:
    from openerp.addons.server_environment import serv_config
except ImportError:
    logging.getLogger('openerp.module').warning(
        'server_environment not available in addons path. '
        'server_env_connector_file will not be usable')

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    """ Specific S3 version of the file import backend """
    _inherit = "account.journal"

    @api.multi
    def _get_s3_config(self):
        global_section_name = self._name.replace('.', '_')

        for journal in self:
            values = {}
            section_name = '.'.join((global_section_name,
                                     journal.name))
            if serv_config.has_section(global_section_name):
                values.update(
                    serv_config.items(global_section_name))
            if serv_config.has_section(section_name):
                values.update(
                    serv_config.items(section_name))

            for field in values.keys():
                self[field] = values[field]

    s3_import = fields.Boolean(
        string="S3 bucket used for automatic import")

    s3_access_key = fields.Char(
        compute=_get_s3_config,
        string='Amazon S3 Access Key')

    s3_secret_access_key = fields.Char(
        compute=_get_s3_config,
        string='Amazon S3 Secret Access Key')

    s3_bucket_name = fields.Char(
        compute=_get_s3_config,
        string='Amazon S3 Bucket Name')

    s3_input_folder = fields.Char(
        compute=_get_s3_config,
        string='Amazon S3 Input folder')

    s3_failed_folder = fields.Char(
        compute=_get_s3_config,
        string='Amazon S3 Failed folder')

    s3_archive_folder = fields.Char(
        compute=_get_s3_config,
        string='Amazon S3 Archive folder')

    @api.multi
    def s3_multi_move_import(self):
        journals = self.search([('s3_import', '=', True)])
        for journal in journals:
            s3 = S3Connection(
                aws_access_key_id=journal.s3_access_key,
                aws_secret_access_key=journal.s3_secret_access_key
            )
            s3_bucket = s3.get_bucket(journal.s3_bucket_name)
            for s3_key in s3_bucket.list(journal.s3_input_folder):
                destination_folder = journal.s3_archive_folder
                try:
                    file_name = s3_key.name
                    data = s3_key.get_contents_as_string()
                    # Only get file name, not path, for reference
                    __, small_file_name = os.path.split(file_name)
                    __, ftype = os.path.splitext(small_file_name)
                    encoded_data = base64.b64encode(data)
                    journal.with_context(
                        file_name=small_file_name
                    ).multi_move_import(encoded_data, ftype.replace('.', ''))
                except Exception as exc:
                    # Move file to "failed"
                    destination_folder = journal.s3_failed_folder
                    _logger.exception(exc)
                finally:
                    # Copy object in new folder + remove old object
                    new_file_name = file_name.replace(journal.s3_input_folder,
                                                      destination_folder)
                    s3_bucket.copy_key(new_file_name,
                                       journal.s3_bucket_name,
                                       file_name)
                    s3_bucket.delete_key(s3_key)
