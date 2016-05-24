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
"""FTP Policy."""

from boto.s3.connection import S3Connection
import os
import base64
from psycopg2 import IntegrityError

from ..backend import file_import_s3
from openerp.addons.connector_file.unit.policy import FileGetterPolicy
from openerp.addons.connector_file.exceptions import InvalidFileError


@file_import_s3
class S3FileGetterPolicy(FileGetterPolicy):

    """Amazon S3 File Getter Policy.

    Manages our interactions with an Amazon S3 bucket

    """

    _model_name = 'ir.attachment.binding'

    def _get_host(self):
        pass

    @staticmethod
    def _ask_files(access_key, secret_access_key, bucket_name,
                   s3_input_folder):
        s3 = S3Connection(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key
        )
        s3_bucket = s3.get_bucket(bucket_name)
        for s3_key in s3_bucket.list(s3_input_folder):
            yield (s3_key.name, '')

    def ask_files(self):
        """Return a generator of S3 objects"""
        return self._ask_files(
            self.backend_record.s3_access_key,
            self.backend_record.s3_secret_access_key,
            self.backend_record.s3_bucket_name,
            self.backend_record.s3_input_folder)

    @staticmethod
    def _get_content(data_file_name, access_key, secret_access_key,
                     bucket_name):
        s3 = S3Connection(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key
        )
        s3_bucket = s3.get_bucket(bucket_name)
        s3_key = s3_bucket.get_key(data_file_name)
        return s3_key.get_contents_as_string()

    def get_hash(self, hash_file_name):
        """Return the external hash of the file."""
        return False

    def get_content(self, data_file_name):
        """Return the raw content of the file."""
        return self._get_content(
            data_file_name,
            self.backend_record.s3_access_key,
            self.backend_record.s3_secret_access_key,
            self.backend_record.s3_bucket_name)

    def manage_exception(self, e, data_file_name, hash_file_name):
        """In case of trouble, try to move the file away."""
        if isinstance(e, InvalidFileError):
            self.move_one(
                data_file_name,
                self.backend_record.s3_input_folder,
                self.backend_record.s3_failed_folder,
            )
        else:
            raise

    def create_one(self, data_file_name, hash_file_name, external_hash,
                   content):
        """Create one file in OpenERP.

        Return id of the created object.

        """
        self.session.cr.execute('SAVEPOINT create_attachment')
        initial_log_exceptions = self.session.cr._default_log_exceptions
        self.session.cr._default_log_exceptions = False
        file_name = os.path.basename(data_file_name)
        try:
            created_id = self.session.create(self.model._name, {
                'name': file_name,
                'datas_fname': os.path.basename(file_name),
                'datas': base64.b64encode(content),
                'backend_id': self.backend_record.id,
            })
        except IntegrityError as e:
            if 'ir_attachment_binding_document_binding_uniq' in e.message:
                # we want our job to be idempotent: if the attachment cannot be
                # created because it already exists, we do nothing.
                # TODO: this actually is inefficient because we download the
                # whole file content and then decide not to create it.
                self.session.cr.execute(
                    'ROLLBACK TO SAVEPOINT create_attachment'
                )
                return None
            else:
                self.session.cr.execute('RELEASE SAVEPOINT create_attachment')
                raise
        finally:
            self.session.cr._default_log_exceptions = initial_log_exceptions

        if self.backend_record.s3_archive_folder:
            self.move_one(
                data_file_name,
                self.backend_record.s3_input_folder,
                self.backend_record.s3_archive_folder,
            )

        return created_id

    def move_one(self, file_name, folder_from, folder_to):
        """Move a file. Return whatever comes from the library."""
        return self._move_one(
            self.backend_record.s3_access_key,
            self.backend_record.s3_secret_access_key,
            self.backend_record.s3_bucket_name,
            file_name,
            folder_from,
            folder_to)

    @staticmethod
    def _move_one(access_key, secret_access_key, bucket_name,
                  file_name, folder_from, folder_to):
        s3 = S3Connection(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key
        )
        s3_bucket = s3.get_bucket(bucket_name)
        # Bucket name must be in copy_source
        s3_key = s3_bucket.get_key(file_name)
        new_file_name = file_name.replace(folder_from, folder_to)

        # Copy object in new folder + remove old _move_one
        s3_bucket.copy_key(new_file_name, bucket_name, file_name)
        s3_bucket.delete_key(s3_key)
