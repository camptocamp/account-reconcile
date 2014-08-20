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
    qoqa.accounting.issuance   -> account.move
    qoqa.promo.issuance.line   -> account.move.line
    qoqa.voucher.issuance.line -> account.move.line

    API:
    /api/v1/promo_accounting_group


"""

from __future__ import division

import logging

from openerp.tools.translate import _
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.exception import (IDMissingInBackend,
                                                MappingError
                                                )
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.backend_adapter import BackendAdapter
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  ImportMapChild,
                                                  )
from ..exception import QoQaError
from ..connector import get_environment, iso8601_to_utc_datetime
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        )
from ..unit.mapper import iso8601_to_utc

_logger = logging.getLogger(__name__)


@job
def import_accounting_issuance(session, model_name, backend_id, qoqa_id, force=False):
    """ Import an accounting issuance group from QoQa """
    env = get_environment(session, model_name, backend_id)
    dispatcher = env.get_connector_unit(AccountingIssuanceDispatcher)
    dispatcher.dispatch(qoqa_id, force=force)


@qoqa
class AccountingIssuanceBatchImporter(DelayedBatchImport):
    """ Import the QoQa Accounting Issuances.

    For every id in in the list of moves, a delayed job is created.
    Import from a date

    """
    _model_name = 'qoqa.accounting.issuance',

    def _import_record(self, record_id, **kwargs):
        """ Delay the import of the records"""
        import_accounting_issuance.delay(self.session,
                                         self.model._name,
                                         self.backend_record.id,
                                         record_id,
                                         **kwargs)


@qoqa
class AccountingIssuanceDispatcher(ConnectorUnit):
    """ Call the correct importer whether the move is promo or voucher. """

    _model_name = 'qoqa.accounting.issuance'

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(AccountingIssuanceDispatcher, self).__init__(environment)
        self.qoqa_id = None
        self.qoqa_record = None

    def _get_base_importer(self):
        assert self.qoqa_record['voucher_id'] or self.qoqa_record['promo_id']
        assert not(self.qoqa_record['voucher_id'] and
                   self.qoqa_record['promo_id'])
        if self.qoqa_record['promo_id']:
            return PromoIssuanceImporter
        else:
            return VoucherIssuanceImporter

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
        importer = self.get_connector_unit_for_model(self._get_base_importer())
        return importer.run(qoqa_id, force=force, record=self.qoqa_record)


class BaseIssuanceImporter(QoQaImportSynchronizer):

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
            super(BaseIssuanceImporter, self)._import(binding_id)

    def _is_uptodate(self, binding_id):
        # already imported, skip it (unless if `force` is used)
        assert self.qoqa_record
        if self.binder.to_openerp(self.qoqa_id) is not None:
            return True

    def _import_dependencies(self):
        """ Import the dependencies for the record """
        assert self.qoqa_record
        rec = self.qoqa_record
        self._import_dependency(rec['user_id'], 'qoqa.res.partner')


@qoqa
class PromoIssuanceImporter(BaseIssuanceImporter):
    _model_name = 'qoqa.accounting.issuance'

    @property
    def mapper(self):
        if self._mapper is None:
            get_unit = self.environment.get_connector_unit
            self._mapper = get_unit(PromoIssuanceMapper)
        return self._mapper


@qoqa
class VoucherIssuanceImporter(BaseIssuanceImporter):
    _model_name = 'qoqa.accounting.issuance'

    @property
    def mapper(self):
        if self._mapper is None:
            get_unit = self.environment.get_connector_unit
            self._mapper = get_unit(VoucherIssuanceMapper)
        return self._mapper


class BaseIssuanceMapper(ImportMapper):

    def _specific_move_values(self, record):
        """ Values of the moves which depend on the promo / vouchers

        :return: browse_record of journal, ref

        """
        raise NotImplementedError

    @mapping
    def move_values(self, record):
        cr, uid = self.session.cr, self.session.uid
        context = self.session.context

        journal, ref = self._specific_move_values(record)

        parsed = iso8601_to_utc_datetime(record['created_at'])
        date = parsed.date().strftime(DEFAULT_SERVER_DATE_FORMAT)
        company_binder = self.get_binder_for_model('res.company')
        company_id = company_binder.to_openerp(record['company_id'])
        assert company_id

        move_obj = self.session.pool['account.move']
        vals = move_obj.account_move_prepare(cr, uid, journal.id, date=date,
                                             ref=ref, company_id=company_id,
                                             context=context)
        return vals

    def _partner_id(self, map_record):
        binder = self.get_binder_for_model('qoqa.res.partner')
        partner_id = binder.to_openerp(map_record.source['user_id'],
                                       unwrap=True)
        assert partner_id, \
            "user_id should have been imported in import_dependencies"
        return partner_id

    def _company_id(self, map_record):
        company_binder = self.get_binder_for_model('res.company')
        company_id = company_binder.to_openerp(map_record.source['company_id'])
        assert company_id
        return company_id

    def _currency_id(self, map_record, company_id):
        company = self.session.browse('res.company', company_id)
        binder = self.get_binder_for_model('res.currency')
        currency_id = binder.to_openerp(map_record.source['currency_id'])
        assert currency_id
        if currency_id != company.currency_id.id:
            return currency_id

    def _analytic_account_id(self, map_record):
        binder = self.get_binder_for_model('qoqa.shop')
        shop_id = binder.to_openerp(map_record.source['shop_id'],
                                    unwrap=True)
        assert shop_id, "Unknow shop_id, refresh the Backend's metadata"
        shop = self.session.browse('sale.shop', shop_id)
        return shop.project_id.id

    def _line_options(self, map_record, values):
        options = self.options.copy()
        company_id = self._company_id(map_record)
        journal_id = values['journal_id']
        options.update({
            'journal': self.session.browse('account.journal', journal_id),
            'partner_id': self._partner_id(map_record),
            'company_id': company_id,
            'date': values['date'],
            'analytic_account_id': self._analytic_account_id(map_record),
        })
        currency_id = self._currency_id(map_record, company_id)
        if currency_id:
            options['currency_id'] = currency_id
        return options


@qoqa
class PromoIssuanceMapper(BaseIssuanceMapper):
    _model_name = 'qoqa.accounting.issuance'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ]

    def _specific_move_values(self, record):
        """ Values of the moves which depend on the promo / vouchers

        :return: browse_record of journal, ref

        """
        promo_type = self._promo_type(record)
        journal = promo_type.property_journal_id
        if not journal:
            user = self.session.browse('res.users', self.session.uid)
            raise MappingError('No journal defined for the promo type "%s" '
                               'for company "%s".\n'
                               'Please configure it on the QoQa backend.' %
                               (promo_type.name, user.company_id.name))
        ref = unicode(record['promo_id'])
        return journal, ref

    def _promo_type(self, record):
        promo_binder = self.get_binder_for_model('qoqa.promo.type')
        qpromo_type_id = record['promo_type_id']
        promo_type_id = promo_binder.to_openerp(qpromo_type_id)
        return self.session.browse('qoqa.promo.type', promo_type_id)

    def _product(self, map_record):
        promo_type = self._promo_type(map_record.source)
        return promo_type.product_id

    def finalize(self, map_record, values):
        lines = map_record.source['promo_accountings']
        map_child = self._get_map_child_unit('qoqa.promo.issuance.line')
        options = self._line_options(map_record, values)
        options['product'] = self._product(map_record)
        items = map_child.get_items(lines, map_record,
                                    'qoqa_promo_line_ids',
                                    options=options)
        values['qoqa_promo_line_ids'] = items
        return values


@qoqa
class VoucherIssuanceMapper(BaseIssuanceMapper):
    _model_name = 'qoqa.accounting.issuance'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ]

    def _specific_move_values(self, record):
        """ Values of the moves which depend on the promo / vouchers

        :return: browse_record of journal, ref

        """
        # read the backend record in the company's context
        backend = self.session.browse('qoqa.backend', self.backend_record.id)
        journal = backend.property_voucher_journal_id
        if not journal:
            user = self.session.browse('res.users', self.session.uid)
            raise MappingError('No journal defined for the vouchers for '
                               'company %s.\n'
                               'Please configure it on the QoQa backend.' %
                               user.company_id.name)
        ref = unicode(record['voucher_id'])
        return journal, ref

    def _counterpart(self, items, values):
        """ Create a counterpart for the credit line given by the API.

        The API gives only the credit line, and we create the receivable
        line.

        """
        assert len(items) == 1
        # items is something like: [
        # (0, 0, {'account_id': 1460,
        #         'account_tax_id': 3,
        #         'created_at': '2013-12-19 15:47:28',
        #         'credit': 11.0,
        #         'date': '2013-12-19 15:47:28',
        #         'name': u'Vente bons cadeaux',
        #         'partner_id': 124381,
        #         'updated_at': '2013-12-19 15:47:28'})
        # ]
        line = items[0][2]
        partner_id = line['partner_id']
        partner = self.session.browse('res.partner', partner_id)
        move_line = {
            'journal_id': line['journal_id'],
            'name': line['name'],
            'account_id': line['credit'] > 0 and
                          partner.property_account_receivable.id or
                          partner.property_account_payable.id,
            'partner_id': partner_id,
            'credit': line['debit'] > 0 and line['debit'] or 0,
            'debit': line['credit'] > 0 and line['credit'] or 0,
            'date': line['date'],
        }
        if line.get('currency_id'):
            move_line['currency_id'] = line['currency_id']
        return (0, 0, move_line)

    def finalize(self, map_record, values):
        lines = map_record.source['promo_accountings']
        map_child = self._get_map_child_unit('qoqa.voucher.issuance.line')
        options = self._line_options(map_record, values)
        items = map_child.get_items(lines, map_record,
                                    'qoqa_voucher_line_ids',
                                    options=options)
        values['qoqa_voucher_line_ids'] = items
        values['line_id'] = [self._counterpart(items, values)]
        return values


@qoqa
class PromoIssuanceLineMapChild(ImportMapChild):
    _model_name = 'qoqa.promo.issuance.line'

    def skip_item(self, map_record):
        """ Skip VAT entries since they are generated by OpenERP """
        record = map_record.source
        if record['is_vat']:
            return True
        if not record['amount']:
            return True


class BaseLineMapper(ImportMapper):

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              ('label', 'name'),
              ('id', 'qoqa_id'),
              ]

    @mapping
    def date(self, record):
        return {'date': self.options.date}

    @mapping
    def partner(self, record):
        return {'partner_id': self.options.partner_id}

    @mapping
    def journal(self, record):
        return {'journal_id': self.options.journal.id}

    @mapping
    def currency(self, record):
        if self.options.currency_id:
            return {'currency_id': self.options.currency_id}


@qoqa
class PromoIssuanceLineMapper(BaseLineMapper):
    _model_name = 'qoqa.promo.issuance.line'

    @mapping
    def amount(self, record):
        amount = record['amount'] / 100
        values = {
            'debit': amount if amount > 0 else 0,
            'credit': -amount if amount < 0 else 0,
        }
        return values

    @mapping
    def account(self, record):
        """ Return line's account.

        The account for credit is the product income account.
        The account for debit comes from the journal.

        """
        amount = record['amount']
        assert amount, \
            "lines without amount should be filtered in PromoIssuanceLineMapChild"
        if amount < 0:  # credit
            account = self.options.product.property_account_income
        else:  # debit
            account = self.options.journal.default_debit_account_id
            if not account:
                journal = self.options.journal
                raise MappingError('No Default Debit Account configured on '
                                   'journal [%s] %s' %
                                   (journal.code, journal.name))

        vals = {'account_id': account.id}
        if account.user_type.analytic_policy != 'never':
            vals['analytic_account_id'] = self.options.analytic_account_id
        return vals

    @mapping
    def taxes(self, record):
        """ Return the tax used by QoQa.

        QoQa provides a VAT also on the credit line, but we want it
        only on the debit line.

        """
        amount = record['amount']
        if amount < 0:  # credit
            return
        binder = self.get_binder_for_model('account.tax')
        tax_id = binder.to_openerp(record['vat_id'])
        # tax code may change per line
        return {'account_tax_id': tax_id}


@qoqa
class VoucherIssuanceLineMapper(BaseLineMapper):
    _model_name = 'qoqa.voucher.issuance.line'

    @mapping
    def credit(self, record):
        if record['amount'] > 0:
            return {'debit': record['amount'] / 100}
        else:
            return {'credit': -record['amount'] / 100}

    @mapping
    def credit_account(self, record):
        journal_id = self.options.journal.id
        journal = self.session.browse('account.journal', journal_id)
        if record['amount'] > 0:
            account = journal.default_debit_account_id
        else:
            account = journal.default_credit_account_id
        if not account:
            raise MappingError('No Default Credit/Debit Account configured on '
                               'journal [%s] %s' %
                               (journal.code, journal.name))
        return {'account_id': account.id}
