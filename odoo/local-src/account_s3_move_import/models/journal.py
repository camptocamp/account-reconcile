# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2016 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""Backend Model for Amazon S3.
"""
import logging
import os
import base64
from boto.s3.connection import S3Connection
from openerp import api, fields, models
try:
    from server_environment import serv_config
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
    def _s3_multi_move_import(self):
        for journal in self.filtered(lambda journal: journal.s3_import):
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
                __, ftype = os.path.splitext(file_name)
                encoded_data = base64.b64encode(data)
                journal.with_context(
                    file_name=s3_key.name
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
