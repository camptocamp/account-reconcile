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

import requests
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper
                                                  )
from .backend import qoqa
from .unit.import_synchronizer import (import_batch,
                                       BatchImportSynchronizer,
                                       QoQaImportSynchronizer,
                                       AddCheckpoint,
                                       )
from .unit.backend_adapter import QoQaAdapter, QoQaClient

"""
Models that represent the structure of the QoQa Shops.
We'll have 1 ``qoqa.backend`` (sharing the connection informations probably),
linked to several ``qoqa.shop``.

Both models will act as 'connector.backend', that means that each time we
build an :py:class:`~openerp.addons.connector.connector.Environment`, we'll
pass it either a ``qoqa.backend``, either a ``qoqa.shop``. Each shop will
have a different :py:class:`~openerp.addons.backend.Backend` version.

"""

class qoqa_backend(orm.Model):
    _name = 'qoqa.backend'
    _description = 'QoQa Backend'
    _inherit = 'connector.backend'
    _backend_type = 'qoqa'

    def _select_versions(self, cr, uid, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('v1', 'v1'),
                ]

    _columns = {
        # override because the version has no meaning here
        'version': fields.selection(
            _select_versions,
            string='API Version',
            required=True),
        'default_lang_id': fields.many2one(
            'res.lang',
            'Default Language',
            required=True,
            help="If a default language is selected, the records "
                 "will be imported in the translation of this language.\n"
                 "Note that a similar configuration exists for each shop."),
        'url': fields.char('URL', required=True),
        'client_key': fields.char('Client Key'),
        'client_secret': fields.char('Client Secret'),
        'access_token': fields.char('OAuth Token'),
        'access_token_secret': fields.char('OAuth Token Secret'),
        'debug': fields.boolean('Debug'),
    }

    def check_connection(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)):
            assert len(ids) == 1, "Only 1 ID accepted, got %r" % ids
            ids = ids[0]
        backend = self.browse(cr, uid, ids, context=context)
        args = (backend.url,
                backend.client_key or '',
                backend.client_secret or '',
                backend.access_token or '',
                backend.access_token_secret or '')
        client = QoQaClient(*args, debug=backend.debug)
        url = client.base_url + 'api/' + backend.version + '/me'
        response = client.head(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise orm.except_orm('Error', err)
        raise orm.except_orm('Ok', 'Connection is successful.')

    def synchronize_metadata(self, cr, uid, ids, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        session = ConnectorSession(cr, uid, context=context)
        for backend_id in ids:
            # import directly, do not delay because this
            # is a fast operation, a direct return is fine
            # and it is simpler to import them sequentially
            import_batch(session, 'qoqa.shop', backend_id)
        return True

    def create(self, cr, uid, vals, context=None):
        existing_ids = self.search(cr, uid, [], context=context)
        if existing_ids:
            raise orm.except_orm(
                _('Error'),
                _('Only 1 QoQa configuration is allowed.'))
        return super(qoqa_backend, self).create(cr, uid, vals, context=context)


class qoqa_shop(orm.Model):
    # model created in 'qoqa_deal'
    # we can't add an _inherit from qoqa.binding
    # so we add manually the _columns
    _inherit = 'qoqa.shop'

    _columns = {
        'backend_id': fields.many2one(
            'qoqa.backend',
            'QoQa Backend',
            required=True,
            readonly=True,
            ondelete='restrict'),
        'qoqa_id': fields.char('ID on QoQa'),
        'sync_date': fields.datetime('Last synchronization date'),
        'lang_id': fields.many2one(
            'res.lang',
            'Default Language',
            required=True,
            help="If a default language is selected, the records "
                 "will be imported in the translation of this language.\n"
                 "Note that a similar configuration exists for each shop."),
    }


class sale_shop(orm.Model):
    _inherit = 'sale.shop'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.shop', 'openerp_id',
            string='QoQa Bindings',
            readonly=True),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(sale_shop, self).copy_data(cr, uid, id,
                                                default=default,
                                                context=context)


@qoqa
class QoQaShopAdapter(QoQaAdapter):
    _model_name = 'qoqa.shop'
    _endpoint = 'shops'


@qoqa
class ShopBatchImport(BatchImportSynchronizer):
    """ Import the records directly, without delaying the jobs.

    Import the QoQa Shops

    They are imported directly because this is a rare and fast operation,
    and we don't really bother if it blocks the UI during this time.
    """
    _model_name = 'qoqa.shop'

    def run(self, filters=None):
        """ Run the synchronization """
        records = self.backend_adapter.search(filters, only_ids=False)
        for record in records:
            self._import_record(record)

    def _import_record(self, record):
        """ Import the record directly.

        For the shops, the import does only 1 call to the
        API, it returns the data from all the shops.
        """
        importer = self.get_connector_unit_for_model(ShopImport)
        record_id = record['id']
        importer.run(record_id, record=record)


@qoqa
class ShopImport(QoQaImportSynchronizer):
    """ Import one QoQa Shop (and create a sale.shop via _inherits).

    A record can be given, so the batch import can import all
    the shops at the same time.
    """
    _model_name = 'qoqa.shop'

    def run(self, qoqa_id, force=False, record=None):
        if record is not None:
            self.qoqa_record = record
        return super(ShopImport, self).run(qoqa_id, force=force)

    def _create(self, data):
        openerp_binding_id = super(ShopImport, self)._create(data)
        checkpoint = self.get_connector_unit_for_model(AddCheckpoint)
        checkpoint.run(openerp_binding_id)
        return openerp_binding_id

    def _get_qoqa_data(self):
        """ Return the raw QoQa data for ``self.qoqa_id`` """
        if self.qoqa_record:
            return self.qoqa_record
        else:
            return super(ShopImport, self)._get_qoqa_data()


@qoqa
class ShopImportMapper(ImportMapper):
    _model_name = 'qoqa.shop'

    direct = []
    # XXX maybe should we map: languages

    @mapping
    @only_create
    def company(self, record):
        qoqa_company_id = record['company']['id']
        binder = self.get_binder_for_model('res.company')
        openerp_id = binder.to_openerp(qoqa_company_id)
        return {'company_id': openerp_id}

    @mapping
    def name(self, record):
        name = record['name']
        return {'name': name}

    @mapping
    def backend_id(self, record):
        return {'backend_id': self.backend_record.id}
