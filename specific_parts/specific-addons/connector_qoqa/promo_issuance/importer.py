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

"""
We have several models in OpenERP, but only 1 entry point in the API
to import them all.

We call the adapter of only of them but it returns the data for vouchers
and promos issuances.

::
    Promos:
    qoqa.promo.issuance      -> account.move
    qoqa.promo.issuance.line -> account.move.line

    Vouchers:
    qoqa.voucher.issuance      -> account.move
    qoqa.voucher.issuance.line -> account.move.line

    API:
    /api/v1/promo_accounting


"""

from __future__ import division

import logging

from openerp.tools.translate import _
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.exception import IDMissingInBackend
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.backend_adapter import BackendAdapter
from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  backend_to_m2o,
                                                  ImportMapper,
                                                  )
from ..exception import QoQaError
from ..connector import get_environment
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        )
from ..unit.mapper import iso8601_to_utc, qoqafloat

_logger = logging.getLogger(__name__)


@job
def import_issuance_line(session, model_name, backend_id, qoqa_id, force=False):
    """ Import an issuance line from QoQa """
    env = get_environment(session, model_name, backend_id)
    dispatcher = env.get_connector_unit(IssuanceLineDispatcher)
    dispatcher.dispatch(qoqa_id, force=force)


@qoqa
class IssuanceLineBatchImport(DelayedBatchImport):
    """ Import the QoQa Promo Issuance.

    For every id in in the list of users, a delayed job is created.
    Import from a date
    """
    _model_name = ['qoqa.promo.issuance.line',
                   'qoqa.voucher.issuance.line',
                   ]

    def _import_record(self, record_id, **kwargs):
        """ Delay the import of the records"""
        import_issuance_line.delay(self.session,
                                   self.model._name,
                                   self.backend_record.id,
                                   record_id,
                                   **kwargs)


@qoqa
class IssuanceLineDispatcher(ConnectorUnit):
    """ Call the correct importer whether the line is promo or voucher. """

    _model_name = ['qoqa.promo.issuance.line',
                   'qoqa.voucher.issuance.line',
                   ]

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(IssuanceLineDispatcher, self).__init__(environment)
        self.qoqa_id = None
        self.qoqa_record = None

    def _get_model(self):
        assert self.qoqa_record['voucher_id'] or self.qoqa_record['promo_id']
        assert not(self.qoqa_record['voucher_id'] and
                   self.qoqa_record['promo_id'])
        if self.qoqa_record['promo_id']:
            return 'qoqa.promo.issuance.line'
        else:
            return 'qoqa.voucher.issuance.line'

    def _get_qoqa_data(self):
        """ Return the raw QoQa data for ``self.qoqa_id`` """
        adapter = self.get_connector_unit_for_model(BackendAdapter)
        return adapter.read(self.qoqa_id)

    def dispatch(self, qoqa_id, force=False):
        """ Get the data and calls the correct importer.

        :param qoqa_id: identifier of the record on QoQa
        """
        self.qoqa_id = qoqa_id
        try:
            self.qoqa_record = self._get_qoqa_data()
        except IDMissingInBackend:
            return _('Record does no longer exist in QoQa')
        importer = self.get_connector_unit_for_model(BaseIssuanceImport,
                                                     self._get_model())
        return importer.run(qoqa_id, force=force, record=self.qoqa_record)


class BaseIssuanceImport(QoQaImportSynchronizer):

    def _import(self, binding_id):
        company_binder = self.get_binder_for_model('res.company')
        company_id = company_binder.to_openerp(self.qoqa_record['company_id'])
        assert company_id
        company = self.session.browse('res.company', company_id)
        user = company.connector_user_id
        if not user:
            raise QoQaError('No connector user configured for company %s' %
                            company.name)
        with self.session.change_user(user.id):
            super(BaseIssuanceImport, self)._import(binding_id)


class BaseLineMapper(ImportMapper):

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              (iso8601_to_utc('date'), 'date'),
              ('label', 'name'),
              ]

    @mapping
    def currency(self, record):
        company_binder = self.get_binder_for_model('res.company')
        company_id = company_binder.to_openerp(record['company_id'])
        assert company_id
        company = self.session.browse('res.company', company_id)
        binder = self.get_binder_for_model('res.currency')
        currency_id = binder.to_openerp(record['currency_id'])
        if currency_id != company.currency_id.id:
            return {'currency_id': currency_id}


@qoqa
class PromoIssuanceImport(BaseIssuanceImport):
    _model_name = 'qoqa.promo.issuance'


@qoqa
class PromoIssuanceMapper(ImportMapper):
    _model_name = 'qoqa.promo.issuance'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ]

    @mapping
    def move_vals(self, record):
        cr, uid = self.session.cr, self.session.uid
        context = self.session.context
        journal_id = 44
        date = record['date']
        ref = _('Issuance Promo %s') % record['promo_id']
        company_binder = self.get_binder_for_model('res.company')
        company_id = company_binder.to_openerp(record['company_id'])
        assert company_id

        move_obj = self.session.pool['account.move']
        vals = move_obj.account_move_prepare(cr, uid, journal_id, date=date,
                                             ref=ref, company_id=company_id,
                                             context=context)
        return vals


@qoqa
class PromoIssuanceLineImport(BaseIssuanceImport):
    _model_name = 'qoqa.promo.issuance.line'

    def _import_promo(self):
        """ Create a move for the lines.

        Pass the full record to the importer so it can use any
        values.

        """
        promo_id = self.qoqa_record['promo_id']
        binder = self.get_binder_for_model('qoqa.promo.issuance')
        if binder.to_openerp(promo_id) is None:
            importer = self.get_connector_unit_for_model(
                BaseIssuanceImport, model='qoqa.promo.issuance')
            importer.run(promo_id, record=self.qoqa_record)

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        self._import_promo()


@qoqa
class PromoIssuanceLineMapper(BaseLineMapper):
    _model_name = 'qoqa.promo.issuance.line'

    direct = (BaseLineMapper.direct +
              [(backend_to_m2o('promo_id', binding='qoqa.promo.issuance'),
                'move_id'),
               ])

    @mapping
    def amount(self, record):
        # TODO: can be either credit either debit
        # no sign in the API currently
        return {'debit': record['amount'] / 100}

    @mapping
    def account(self, record):
        return {'account_id': 1483}

    @mapping
    def partner_id(self, record):
        return {'partner_id': False}

    @mapping
    def taxes(self, record):
        binder = self.get_binder_for_model('account.tax')
        tax_id = binder.to_openerp(record['vat_id'])
        # tax code may change per line
        return {'account_tax_id': tax_id}


@qoqa
class VoucherIssuanceImport(BaseIssuanceImport):
    _model_name = 'qoqa.voucher.issuance'


@qoqa
class VoucherIssuanceMapper(ImportMapper):
    _model_name = 'qoqa.voucher.issuance'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ]

    @mapping
    def move_vals(self, record):
        cr, uid = self.session.cr, self.session.uid
        context = self.session.context
        journal_id = 44
        date = record['date']
        ref = _('Issuance Voucher %s') % record['voucher_id']
        company_binder = self.get_binder_for_model('res.company')
        company_id = company_binder.to_openerp(record['company_id'])
        assert company_id

        move_obj = self.session.pool['account.move']
        vals = move_obj.account_move_prepare(cr, uid, journal_id, date=date,
                                             ref=ref, company_id=company_id,
                                             context=context)
        return vals


@qoqa
class VoucherIssuanceLineImport(BaseIssuanceImport):
    _model_name = 'qoqa.voucher.issuance.line'

    def _import_voucher(self):
        """ Create a move for the lines.

        Pass the full record to the importer so it can use any
        values.

        """
        voucher_id = self.qoqa_record['voucher_id']
        binder = self.get_binder_for_model('qoqa.voucher.issuance')
        if binder.to_openerp(voucher_id) is None:
            importer = self.get_connector_unit_for_model(
                BaseIssuanceImport, model='qoqa.voucher.issuance')
            importer.run(voucher_id, record=self.qoqa_record)

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        self._import_voucher()

    def _after_import(self, binding_id):
        """ Hook called at the end of the import """
        line = self.session.browse(self.model._name, binding_id).openerp_id
        self._create_counterpart(line)

    def _create_counterpart(self, line):
        move_line = {
            'journal_id': line.journal_id.id,
            'period_id': line.period_id.id,
            'name': line.name,
            'account_id': 1483,  # TODO
            'move_id': line.move_id.id,
            'partner_id': line.partner_id.id if line.partner_id else False,
            'currency_id': line.currency_id.id if line.currency_id else False,
            'credit': 0,
            'debit': line.credit,
            'date': line.date,
        }
        self.session.create('account.move.line', move_line)


@qoqa
class VoucherIssuanceLineMapper(BaseLineMapper):
    _model_name = 'qoqa.voucher.issuance.line'

    direct = (BaseLineMapper.direct +
              [(backend_to_m2o('voucher_id', binding='qoqa.voucher.issuance'),
                'move_id'),
               (qoqafloat('amount'), 'credit'),
               ])

    @mapping
    def account(self, record):
        return {'account_id': 1483}

    @mapping
    def partner_id(self, record):
        return {'partner_id': False}

    @mapping
    def taxes(self, record):
        binder = self.get_binder_for_model('account.tax')
        tax_id = binder.to_openerp(record['vat_id'])
        # tax code may change per line
        return {'account_tax_id': tax_id}
