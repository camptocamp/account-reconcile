# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer
from openerp.addons.connector.unit.backend_adapter import BackendAdapter

from ..connector import get_environment
from ..backend import qoqa
from ..sale.payment_id_importer import ImportPaymentId


@qoqa
class RefundExporter(ExportSynchronizer):
    _model_name = 'account.invoice'

    def run(self, refund_id):
        """ Create a refund on the QoQa backend """
        refund = self.session.browse(self.model._name, refund_id)
        if refund.transaction_id:
            return _('Already a transaction ID for this refund')
        invoice = refund.refund_from_invoice_id
        if not invoice:
            return _('No origin invoice')
        sales = invoice.sale_order_ids
        if not sales or not sales[0].qoqa_bind_ids:
            return _('Not a sale from the QoQa backend')
        qsale = sales[0].qoqa_bind_ids[0]
        origin_payment_id = qsale.qoqa_payment_id
        if not origin_payment_id:
            # the payment_id has not been imported during the historic
            # import, retrieve it using a special importer
            importer = self.get_connector_unit_for_model(
                ImportPaymentId, 'qoqa.sale.order')
            importer.get_payment_id(qsale.id)
            qsale.refresh()
            origin_payment_id = qsale.qoqa_payment_id
        if not origin_payment_id:
            raise orm.except_orm(
                _('Error'),
                _('Cannot be refund on the QoQa backend because '
                  'no payment ID could be retrieved for the sales order %s') %
                qsale.name)
        adapter = self.get_connector_unit_for_model(BackendAdapter,
                                                    'qoqa.sale.order')
        # qoqa uses 2 digits, expressed in integers
        amount = float_round(refund.amount_total * 100, precision_digits=0)
        payment_id = adapter.refund(qsale.qoqa_id,
                                    origin_payment_id,
                                    int(amount))
        self.session.write(self.model._name, refund_id,
                           {'transaction_id': payment_id})
        # We search move_line to write transaction_ref
        move_line_ids = self.session.search(
            'account.move.line',
            [('move_id', '=', refund.move_id.id),
             ('account_id', '=', refund.account_id.id)])
        # We deactive the account_counstraint check by updating the context
        with self.session.change_context({'from_parent_object': True}):
            self.session.write(
                'account.move.line',
                move_line_ids,
                {'transaction_ref': payment_id})
        return _('Refund created with payment id: %s' % payment_id)


@job
def create_refund(session, model_name, backend_id, refund_id):
    """ Create a refund """
    env = get_environment(session, model_name, backend_id)
    exporter = env.get_connector_unit(RefundExporter)
    return exporter.run(refund_id)
