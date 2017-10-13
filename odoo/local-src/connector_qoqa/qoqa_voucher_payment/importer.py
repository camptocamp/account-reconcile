# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  )
from openerp import fields
from ..backend import qoqa
from ..unit.importer import QoQaImporter
from ..unit.mapper import FromAttributes, iso8601_to_utc

_logger = logging.getLogger(__name__)


@qoqa
class VoucherPaymentImporter(QoQaImporter):
    _model_name = 'qoqa.voucher.payment'

    def __init__(self, environment):
        super(VoucherPaymentImporter, self).__init__(environment)
        self.order_binding = None

    def _is_uptodate(self, binding):
        # Never update a payment, importer would create
        # move lines at double. Anyway, this importer should
        # never be called twice because it is called only
        # by the sales order importer which itself exits
        # when the binding already exist
        if binding:
            return True

    def _create_data(self, map_record, **kwargs):
        """ Get the data to pass to :py:meth:`_create` """
        return super(VoucherPaymentImporter, self)._create_data(
            map_record,
            order_binding=self.order_binding,
        )

    def _import(self, binding, **kwargs):
        self.order_binding = kwargs.pop('order_binding', None)
        assert self.order_binding, "must receive an order_binding"
        return super(VoucherPaymentImporter, self)._import(binding, **kwargs)


@qoqa
class VoucherPaymentImportMapper(ImportMapper, FromAttributes):
    _model_name = 'qoqa.voucher.payment'

    _from_attributes = [
        (iso8601_to_utc('created_at'), 'created_at'),
        (iso8601_to_utc('updated_at'), 'updated_at'),
    ]

    @mapping
    def all(self, record):
        """ Set move and line values

        Example of record:

        ::

            [{u'attributes': {u'accounting_website_id': 3,
                              u'amount': u'29.0',
                              u'company_id': 1,
                              u'created_at': u'2016-12-02T10:45:12.449+01:00',
                              u'currency': u'chf',
                              u'description': u'test gb',
                              u'free_shipping': False,
                              u'main_type': u'voucher',
                              u'sub_type': u'customer_service',
                              u'updated_at': u'2016-12-02T10:45:12.449+01:00'},
              u'id': u'556507',
              u'type': u'discount'}]

        """
        attributes = record['attributes']
        date = fields.datetime.now()
        order_binding = self.options.order_binding
        assert order_binding, \
            "need an order_binding to create a voucher payment"
        values = {
            'qoqa_order_id': order_binding.id,
            'ref': order_binding.name,
            'company_id': order_binding.company_id.id,
            'date': date,
        }

        payment_mode = order_binding.payment_mode_id
        order_journal = payment_mode.fixed_journal_id

        description = u'%s (%s)' % (attributes['description'], record['id'])
        partner = order_binding.partner_id.commercial_partner_id
        amount = float(attributes['amount'])
        voucher_journal = self.backend_record.property_voucher_journal_id
        values['journal_id'] = voucher_journal.id
        lines = [
            # payment line (voucher)
            {'account_id': voucher_journal.default_debit_account_id.id,
             'name': description,
             'partner_id': partner.id,
             'debit': amount,
             'credit': 0.0,
             },
            # receivable
            {'account_id': order_journal.default_credit_account_id.id,
             'name': description,
             'partner_id': partner.id,
             'debit': 0.0,
             'credit': amount,
             }]
        values['line_ids'] = [(0, 0, line) for line in lines]
        return values
