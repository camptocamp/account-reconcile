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

from openerp.osv import orm, fields
try:
    from server_environment import serv_config
except ImportError:
    logging.getLogger('openerp.module').warning(
        'server_environment not available in addons path. '
        'server_env_connector_file will not be usable')

_logger = logging.getLogger(__name__)


class file_import_s3_backend(orm.Model):
    """ Specific S3 version of the file import backend """
    _name = "file_import.backend"
    _inherit = "file_import.backend"

    def _select_versions(self, cr, uid, context=None):
        """Parent model inheritance (needs redefinition)."""
        return super(file_import_s3_backend,
                     self)._select_versions(cr, uid, context=context) + [
            ('s3_1', 'Amazon S3 v1')]

    def _get_environment_config_by_name(self, cr, uid, ids, field_names,
                                        arg, context=None):
        values = {}
        for backend in self.browse(cr, uid, ids, context=context):
            values[backend.id] = {}
            for field_name in field_names:
                section_name = '.'.join((self._name.replace('.', '_'),
                                         backend.name))
                try:
                    value = serv_config.get(section_name, field_name)
                    values[backend.id][field_name] = value
                except:
                    _logger.exception('error trying to read field %s '
                                      'in section %s', field_name,
                                      section_name)
                    values[backend.id][field_name] = False
        return values

    _columns = {
        'version': fields.selection(_select_versions,
                                    string='Version',
                                    required=True),
        's3_access_key': fields.function(
            _get_environment_config_by_name,
            string='Amazon S3 Access Key',
            type='char',
            multi='connection_config'),
        's3_secret_access_key': fields.function(
            _get_environment_config_by_name,
            string='Amazon S3 Secret Access Key',
            type='char',
            multi='connection_config'),
        's3_bucket_name': fields.function(
            _get_environment_config_by_name,
            string='Amazon S3 Bucket Name',
            type='char',
            multi='connection_config'),
        's3_input_folder': fields.function(
            _get_environment_config_by_name,
            string='Amazon S3 Input folder',
            type='char',
            multi='connection_config'),
        's3_failed_folder': fields.function(
            _get_environment_config_by_name,
            string='Amazon S3 Failed folder',
            type='char',
            multi='connection_config'),
        's3_archive_folder': fields.function(
            _get_environment_config_by_name,
            string='Amazon S3 Archive folder',
            type='char',
            multi='connection_config'),
    }
