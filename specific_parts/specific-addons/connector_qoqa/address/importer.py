# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

import logging

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  backend_to_m2o,
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        )
from ..unit.mapper import iso8601_to_utc

_logger = logging.getLogger(__name__)


@qoqa
class AddressBatchImport(DelayedBatchImport):
    """ Import the QoQa Users.

    For every id in in the list of users, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.address'


@qoqa
class AddressImport(QoQaImportSynchronizer):
    _model_name = 'qoqa.address'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        self._import_dependency(rec['user_id'], 'qoqa.res.partner')

    def _import(self, binding_id):
        if binding_id is None:
            # this is to handle a particular scenario:
            # `_get_binding_id` is called at the beginning of the
            # importer. When we import the dependencies, if the partner
            # was not present, it is imported. The import of the partner
            # will import itself all the addresses, including this one.
            # so we get its binding ID in order to not create a new
            # address and ends up with a "unique constraint error".
            binding_id = self._get_binding_id()
        return super(AddressImport, self)._import(binding_id)


@qoqa
class AddressImportMapper(ImportMapper):
    _model_name = 'qoqa.address'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              (backend_to_m2o('user_id', binding='qoqa.res.partner'), 'parent_id'),
              ('street', 'street'),
              ('street2', 'street2'),
              ('code', 'zip'),
              ('city', 'city'),
              (backend_to_m2o('country_id'), 'country_id'),
              ('phone', 'phone'),
              ('mobile', 'mobile'),
              ('fax', 'fax'),
              ('is_active', 'active'),
              ('digicode', 'digicode'),
              ]

    @mapping
    def qoqa_address(self, record):
        return {'qoqa_address': True}

    @mapping
    @only_create
    def company(self, record):
        return {'company_id': False}

    @mapping
    def name(self, record):
        parts = [part for part in (record['firstname'], record['lastname'])
                 if part]
        name = ' '.join(parts)
        return {'name': name}

    @only_create
    @mapping
    def type(self, record):
        return {'type': 'contact'}

    @only_create
    @mapping
    def customer(self, record):
        return {'customer': True}
