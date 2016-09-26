# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import _, exceptions
from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.unit.synchronizer import Exporter
from openerp.addons.connector.unit.backend_adapter import BackendAdapter

from ..connector import get_environment
from ..backend import qoqa
from ..related_action import unwrap_binding


@qoqa
class RefundExporter(Exporter):
    _model_name = 'account.invoice'

    def run(self, refund_id):
        """ Create a refund on the QoQa backend """
        refund = self.model.browse(refund_id)
        if refund.transaction_id:
            return _('Already a transaction ID for this refund')
        if refund.state == 'cancel':
            return _('The refund has been cancelled.')
        invoice = refund.refund_from_invoice_id
        if not invoice:
            return _('No origin invoice')
        sales = invoice.sale_order_ids
        if not sales or not sales[0].qoqa_bind_ids:
            return _('Not a sale from the QoQa backend')
        qsale = sales[0].qoqa_bind_ids[0]
        origin_payment_id = qsale.qoqa_payment_id
        if not origin_payment_id:
            raise exceptions.UserError(
                _('Cannot be refund on the QoQa backend because '
                  'no payment ID could be retrieved for the sales order %s') %
                qsale.name)
        adapter = self.unit_for(BackendAdapter, 'qoqa.payment')
        payment = adapter.refund(origin_payment_id,
                                 refund.amount_total)
        payment_id = payment['data']['id']
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
    with get_environment(session, model_name, backend_id) as conn_env:
        exporter = conn_env.get_connector_unit(RefundExporter)
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
        origin_payment_id = refund.transaction_id
        if not origin_payment_id:
            return
        adapter = self.unit_for(BackendAdapter, 'qoqa.credit.note')

        result = adapter.cancel(origin_payment_id)
        if not result:
            raise exceptions.UserError(
                _('Credit note could not be cancelled')
            )
        return _('Canceled refund with payment id: %s' % origin_payment_id)


@job(default_channel='root.connector_qoqa.fast')
@related_action(action=unwrap_binding, id_pos=3)
def cancel_refund(session, model_name, backend_id, refund_id):
    """ Cancel a refund """
    with get_environment(session, model_name, backend_id) as conn_env:
        exporter = conn_env.get_connector_unit(CancelRefundExporter)
        return exporter.run(refund_id)
