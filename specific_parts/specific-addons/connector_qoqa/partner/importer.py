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
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        )
from ..unit.mapper import iso8601_to_utc

_logger = logging.getLogger(__name__)


@qoqa
class ResPartnerBatchImport(DelayedBatchImport):
    """ Import the QoQa Users.

    For every id in in the list of users, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.res.partner'


@qoqa
class ResPartnerImport(QoQaImportSynchronizer):
    _model_name = 'qoqa.res.partner'


@qoqa
class ResPartnerImportMapper(ImportMapper):
    _model_name = 'qoqa.res.partner'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ('suspicious', 'suspicious'),
              ('is_active', 'qoqa_active'),
              ('email', 'email'),
              ('name', 'qoqa_name'),
              ]

    @only_create
    @mapping
    def name(self, record):
        name = ' '.join((record['firstname'], record['lastname']))
        return {'name': name}

    @mapping
    def use_parent_address(self, record):
        return {'use_parent_address': False}

    @only_create
    @mapping
    def type(self, record):
        return {'type': 'default'}

    @only_create
    @mapping
    def customer(self, record):
        return {'customer': True}

    @only_create
    @mapping
    def language(self, record):
        """ french by default """
        return {'lang': 'fr_FR'}

    @only_create
    @mapping
    def is_company(self, record):
        """ partners are companies so we can bind addresses on them """
        return {'is_company': True}

    @only_create
    @mapping
    def openerp_id(self, record):
        """ Will bind the customer on a existing partner
        with the same email """
        sess = self.session
        partner_ids = sess.search('res.partner',
                                  [('email', '=', record['email']),
                                   ('customer', '=', True),
                                   ('is_company', '=', True)])
        if partner_ids:
            return {'openerp_id': partner_ids[0]}
