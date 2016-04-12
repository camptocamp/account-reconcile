# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import exceptions, _
from openerp.tools.float_utils import float_round
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.unit.synchronizer import Exporter
from openerp.addons.connector.unit.backend_adapter import BackendAdapter

from ..connector import get_environment
from ..backend import qoqa
# from ..sale.payment_id_importer import ImportPaymentId
from ..related_action import unwrap_binding


@qoqa
class RefundExporter(Exporter):
    _model_name = 'account.invoice'

    def run(self, refund_id):
        """ Create a refund on the QoQa backend """
        refund = self.model.browse(refund_id)
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
        # TODO: see if it still happens in 2016...
        # if not origin_payment_id:
        #     # the payment_id has not been imported during the historic
        #     # import, retrieve it using a special importer
        #     importer = self.unit_for(ImportPaymentId, 'qoqa.sale.order')
        #     importer.get_payment_id(qsale.id)
        #     origin_payment_id = qsale.qoqa_payment_id
        if not origin_payment_id:
            raise exceptions.UserError(
                _('Cannot be refund on the QoQa backend because '
                  'no payment ID could be retrieved for the sales order %s') %
                qsale.name)
        adapter = self.unit_for(BackendAdapter, 'qoqa.sale.order')
        # qoqa uses 2 digits, expressed in integers
        amount = float_round(refund.amount_total * 100, precision_digits=0)
        payment_id = adapter.refund(qsale.qoqa_id,
                                    origin_payment_id,
                                    int(amount))
        refund.write({'transaction_id': payment_id})
        # We search move_line to write transaction_ref
        move_lines = self.env['account.move.line'].search(
            [('move_id', '=', refund.move_id.id),
             ('account_id', '=', refund.account_id.id)]
        )
        # TODO: check if we still have account_constraint
        # We deactive the account_constraint check by updating the context
        move_lines.with_context(from_parent_object=True).write(
            {'transaction_ref': payment_id}
        )
        return _('Refund created with payment id: %s' % payment_id)


@job(default_channel='root.connector_qoqa.fast')
@related_action(action=unwrap_binding, id_pos=3)
def create_refund(session, model_name, backend_id, refund_id):
    """ Create a refund """
    env = get_environment(session, model_name, backend_id)
    exporter = env.get_connector_unit(RefundExporter)
    return exporter.run(refund_id)


@qoqa
class CancelRefundExporter(Exporter):
    _model_name = 'account.invoice'

    def run(self, refund_id):
        """ Get the refund to cancel """
        refund = self.model.browse(refund_id)
        invoice = refund.refund_from_invoice_id
        if not invoice:
            return _('No origin invoice')
        sales = invoice.sale_order_ids
        if not sales or not sales[0].qoqa_bind_ids:
            return _('Not a sale from the QoQa backend')
        qsale = sales[0].qoqa_bind_ids[0]
        origin_payment_id = refund.transaction_id

        if not origin_payment_id:
            raise exceptions.UserError(
                _('Cannot be cancel on the QoQa backend because '
                  'no payment ID could be retrieved for the sales order %s') %
                qsale.name)
        adapter = self.unit_for(BackendAdapter, 'qoqa.sale.order')

        payment_id = adapter.cancel_refund(qsale.qoqa_id, origin_payment_id)
        return _('Cancel refund with payment id: %s' % payment_id)


@job(default_channel='root.connector_qoqa.fast')
@related_action(action=unwrap_binding, id_pos=3)
def cancel_refund(session, model_name, backend_id, refund_id):
    """ Cancel a refund """
    env = get_environment(session, model_name, backend_id)
    exporter = env.get_connector_unit(CancelRefundExporter)
    return exporter.run(refund_id)
