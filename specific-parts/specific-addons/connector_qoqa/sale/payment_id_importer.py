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

""" Import payment ids on existing qoqa sales orders

The payment_id has been imported on the sales orders since early 2014,
but is missing for the ones earlier than 2014.  It is required when
we want to do a refund.  So, this importer retrieve and update the field
when called on a qoqa sales order.

"""

import logging

from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.exception import FailedJobError
from ..connector import historic_import, get_environment
from ..backend import qoqa
from ..unit.backend_adapter import QoQaAdapter
from .importer import _get_payment_method

_logger = logging.getLogger(__name__)


@qoqa
class ImportPaymentId(ConnectorUnit):
    _model_name = 'qoqa.sale.order'

    def get_payment_id(self, binding_id):
        binding = self.session.browse(self.model._name,
                                      binding_id)
        if binding.qoqa_payment_id:
            return
        adapter = self.get_connector_unit_for_model(QoQaAdapter)
        qoqa_record = adapter.read(binding.qoqa_id)
        vals = self.payment_method(qoqa_record)
        if not vals:
            return  # payment on wrong company / no payment
        with self.session.change_context({'connector_no_export': True}):
            self.session.write(self.model._name,
                               binding_id,
                               vals)
            # update linked invoices
            for invoice in binding.invoice_ids:
                invoice.write({'transaction_id': vals['transaction_id']})

    def payment_method(self, record):
        qpayments = record['payments']
        qshop_binder = self.get_binder_for_model('qoqa.shop')
        qshop_id = qshop_binder.to_openerp(record['shop_id'])
        qshop = self.session.read('qoqa.shop', qshop_id, ['company_id'])
        company_id = qshop['company_id'][0]
        try:
            methods = ((payment, _get_payment_method(self, payment, company_id))
                       for payment in qpayments)
        except FailedJobError:
            if historic_import(self, record).historic:
                # Sometimes, an offer is on the FR website
                # but paid with postfinance. Forgive them for the
                # historical sales orders.
                return
            raise
        methods = (method for method in methods if method[1])
        methods = sorted(methods, key=lambda m: m[1].sequence)
        if not methods:
            return
        method = methods[0]
        transaction_id = method[0].get('transaction')
        return {'qoqa_transaction': transaction_id,
                # keep as payment's reference
                'qoqa_payment_id': method[0]['id'],
                # used for the reconciliation (transfered to invoice)
                'transaction_id': method[0]['id']}


@job
def import_payment_id(session, model_name, backend_id, binding_id):
    """ Fix the missing payment_id on a qoqa sale order """
    env = get_environment(session, model_name, backend_id)
    importer = env.get_connector_unit(ImportPaymentId)
    importer.get_payment_id(binding_id)
