# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.importer import DelayedBatchImporter, QoQaImporter
from ..unit.mapper import FromDataAttributes, iso8601_to_utc

_logger = logging.getLogger(__name__)


@qoqa
class AddressBatchImport(DelayedBatchImporter):
    """ Import the QoQa Users.

    For every id in in the list of users, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.address'


@qoqa
class AddressImporter(QoQaImporter):
    _model_name = 'qoqa.address'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        qoqa_user_id = rec['data']['attributes']['user_id']
        self._import_dependency(qoqa_user_id, 'qoqa.res.partner')


@qoqa
class AddressImportMapper(ImportMapper, FromDataAttributes):
    _model_name = 'qoqa.address'

    direct = []

    from_data_attributes = [
        ('street', 'street'),
        ('street2', 'street2'),
        ('zip', 'zip'),
        ('city', 'city'),
        ('phone', 'phone'),
        ('digicode', 'digicode'),
        (iso8601_to_utc('created_at'), 'created_at'),
        (iso8601_to_utc('updated_at'), 'updated_at'),
    ]

    @mapping
    def country(self, record):
        qoqa_country_id = record['data']['attributes']['country_id']
        binder = self.binder_for('res.country')
        country = binder.to_openerp(qoqa_country_id, unwrap=True)
        return {'country_id': country.id}

    @mapping
    def qoqa_address(self, record):
        return {'qoqa_address': True}

    @mapping
    @only_create
    def company(self, record):
        return {'company_id': False}

    @mapping
    def name(self, record):
        attrs = record['data']['attributes']
        parts = [part for part in (attrs['firstname'], attrs['lastname'])
                 if part]
        name = ' '.join(parts)
        return {'name': name}

    @only_create
    @mapping
    def type(self, record):
        # do not set 'contact', otherwise the address fields are shared with
        # the parent
        return {'type': 'other'}

    @only_create
    @mapping
    def customer(self, record):
        return {'customer': True}

    @mapping
    def parent(self, record):
        data = record['data']
        qoqa_user_id = data['attributes']['user_id']
        qoqa_order_user_id = data['attributes']['order_user_id']
        assert qoqa_user_id or qoqa_order_user_id

        vals = {}
        if qoqa_order_user_id:
            # The address comes from a sales order. The website
            # copies the addresses used for sales and remove their
            # user_id link.  The original user of the address is in
            # order_user_id.
            vals.update({
                'active': False,
                'qoqa_order_address': True,
            })

        binder = self.binder_for('qoqa.res.partner')
        parent = binder.to_openerp(qoqa_user_id or qoqa_order_user_id,
                                   unwrap=True)
        assert parent, ("user %s should have been imported "
                        "in dependencies" %
                        (qoqa_user_id or qoqa_order_user_id,))
        vals.update({
            'parent_id': parent.id,
            'lang': parent.lang,
        })
        return vals
