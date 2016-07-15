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
class ResPartnerBatchImporter(DelayedBatchImporter):
    """ Import the QoQa Users.

    For every id in in the list of users, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.res.partner'


@qoqa
class ResPartnerImport(QoQaImporter):
    _model_name = 'qoqa.res.partner'


@qoqa
class ResPartnerImportMapper(ImportMapper, FromDataAttributes):
    _model_name = 'qoqa.res.partner'

    from_data_attributes = [
        ('email', 'email'),
        ('pseudo', 'qoqa_name'),
        (iso8601_to_utc('created_at'), 'created_at'),
        (iso8601_to_utc('updated_at'), 'updated_at'),
    ]

    @mapping
    @only_create
    def company(self, record):
        """ partners are shared between companies """
        return {'company_id': False}

    @mapping
    def name(self, record):
        attrs = record['data'].get('attributes', {})
        login = attrs.get('pseudo')
        email = attrs['email']
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
        return {'type': 'contact'}

    @only_create
    @mapping
    def customer(self, record):
        return {'customer': True}

    @only_create
    @mapping
    def language(self, record):
        attrs = record['data'].get('attributes', {})
        qoqa_lang = attrs.get('locale')
        if not qoqa_lang:
            return {'lang': 'fr_FR'}
        else:
            binder = self.binder_for('res.lang')
            lang = binder.to_openerp(qoqa_lang)
            return {'lang': lang.code}
