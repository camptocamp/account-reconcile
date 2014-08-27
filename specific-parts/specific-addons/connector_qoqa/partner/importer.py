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

    def __init__(self, environment):
        super(ResPartnerImport, self).__init__(environment)
        self.should_create_addresses = None

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        if rec['customer'] and rec['customer']['origin_shop_id']:
            self._import_dependency(rec['customer']['origin_shop_id'],
                                    'qoqa.shop')

    def _get_binding_id(self):
        """Return the binding id from the qoqa id"""
        binding_id = super(ResPartnerImport, self)._get_binding_id()
        if binding_id is None:
            # Create the addresses from the record only on creation
            # of the customer. Especially useful when importing
            # historical sales orders so we can avoid calls for
            # the addresses, by cons, less useful later as we'll
            # need to import separately the modified addresses anyway.
            self.should_create_addresses = True
        return binding_id

    def _after_import(self, binding_id):
        if self.should_create_addresses:
            for address in self.qoqa_record['addresses']:
                importer = self.get_connector_unit_for_model(
                    QoQaImportSynchronizer, 'qoqa.address')
                importer.run(address['id'], record=address)


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

    @mapping
    @only_create
    def company(self, record):
        """ partners are shared between companies """
        return {'company_id': False}

    @mapping
    def name(self, record):
        """ The 'firstname' and 'lastname' fields are wrong in QoQa and
        should not be used, instead, we take the login if existing and
        email.
        """
        login = record.get('name')
        email = record['email']
        if login:
            name = "%s (%s)" % (login, email)
        else:
            name = email
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
        if not record['customer']:
            return {'lang': 'fr_FR'}
        else:
            qlang_id = record['customer']['language_id']
            binder = self.get_binder_for_model('res.lang')
            lang_id = binder.to_openerp(qlang_id)
            lang = self.session.browse('res.lang', lang_id)
            return {'lang': lang.code}

    @mapping
    def customer_status(self, record):
        if not record['customer']:
            return
        qstatus_id = record['customer']['status_id']
        binder = self.get_binder_for_model('qoqa.customer.status')
        status = binder.to_openerp(qstatus_id)
        return {'qoqa_status': status}

    @mapping
    def origin_shop(self, record):
        if not record['customer']:
            return
        qshop_id = record['customer']['origin_shop_id']
        if not qshop_id:
            return
        binder = self.get_binder_for_model('qoqa.shop')
        shop_id = binder.to_openerp(qshop_id)
        return {'origin_shop_id': shop_id}

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
