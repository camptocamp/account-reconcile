# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json
import logging
from datetime import date
from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp
from openerp.addons.connector.session import ConnectorSession

from ..unit.backend_adapter import QoQaAdapter, api_handle_errors
from ..backend import qoqa
from .exporter import cancel_sales_order, settle_sales_order


_logger = logging.getLogger(__name__)


class QoqaSaleOrder(models.Model):
    _name = 'qoqa.sale.order'
    _inherit = 'qoqa.binding'
    _inherits = {'sale.order': 'openerp_id'}
    _description = 'QoQa Sale Order'

    openerp_id = fields.Many2one(comodel_name='sale.order',
                                 string='Sales Order',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    created_at = fields.Datetime(string='Created At (on QoQa)', readonly=True)
    updated_at = fields.Datetime(string='Updated At (on QoQa)', readonly=True)
    qoqa_order_line_ids = fields.One2many(
        comodel_name='qoqa.sale.order.line',
        inverse_name='qoqa_order_id',
        string='QoQa Order Lines',
        readonly=True,
    )
    qoqa_amount_total = fields.Float(
        string='Total amount on QoQa',
        digits_compute=dp.get_precision('Account'),
        readonly=True,
    )
    invoice_ref = fields.Char(string='Invoice Ref. on QoQa', readonly=True)
    # id of the main payment on qoqa, used as key for reconciliation
    qoqa_payment_id = fields.Char(string='ID of the payment on QoQa',
                                  readonly=True)
    qoqa_payment_date = fields.Date(string='Date of the payment',
                                    readonly=True,
                                    help="Local date of the payment, "
                                         "used to know if it can be "
                                         "canceled.")
    qoqa_payment_amount = fields.Float(
        string='Amount paid on QoQa',
        digits_compute=dp.get_precision('Account'),
        readonly=True,
    )
    # field with name 'transaction' in the main payment
    qoqa_transaction = fields.Char(string='Transaction number of the payment '
                                          'on QoQa',
                                   readonly=True)

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A sales order can be exported only once on the same backend"),

    ]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.sale.order',
        inverse_name='openerp_id',
        string='QBindings',
    )
    active = fields.Boolean(string='Active', default=True)

    @api.model
    def _prepare_invoice(self):
        values = super(SaleOrder, self)._prepare_invoice()
        if self.qoqa_bind_ids:
            # qoqa_bind_ids is unique, there is a constraint
            binding = self.qoqa_bind_ids
            # keep only the issued invoice from the qoqa backend
            values.update({
                'name': binding.invoice_ref,
                # restore order's name, don't want the concatenated
                # invoices numbers
                'reference': self.name,
                'transaction_id': binding.qoqa_payment_id,
            })
        return values

    @api.multi
    def _call_cancel(self, cancel_direct=False):
        self.ensure_one()
        # only cancel on qoqa if all the cancellations succeeded
        # canceled_in_backend means already canceled on QoQa
        if not self.canceled_in_backend:
            session = ConnectorSession.from_env(self.env)
            for binding in self.qoqa_bind_ids:
                # should be called at the very end of the 'cancel' method so we
                # won't call 'cancel' on qoqa if something failed before
                if cancel_direct:
                    # we want to do a direct call to the API when the payment
                    # can be canceled before midnight because the job may take
                    # too long time to be executed
                    _logger.info("Cancel order %s directly on QoQa",
                                 binding.name)
                    message = _('Impossible to cancel the sales order '
                                'on the backend now.')
                    with api_handle_errors(message):
                        cancel_sales_order(session, binding._model._name,
                                           binding.id)
                else:
                    # no timing issue in this one, the sales order must be
                    # canceled but it can be done later
                    _logger.info("Cancel order %s later (job) on QoQa",
                                 binding.name)
                    cancel_sales_order.delay(session, binding._model._name,
                                             binding.id, priority=1)

    @api.multi
    def action_cancel(self):
        """ Automatically cancel a sales orders and related documents.

        If the sales order has been created and canceled the same day, a
        direct call to the QoQa API will cancel the order, which will
        cancel the payment as well (excepted for Paypal, handled
        manually, hence the ``payment_mode_id.payment_cancellable_on_qoqa``
        field). Otherwise, a refund will be created.
        """
        actions = []
        for order in self:
            cancel_direct = False
            if (order.qoqa_bind_ids and
                    order.payment_mode_id.payment_cancellable_on_qoqa):
                binding = order.qoqa_bind_ids[0]
                # can be canceled only the day of the payment
                payment_date = fields.Date.from_string(
                    binding.qoqa_payment_date
                )
                if payment_date == date.today():
                    cancel_direct = True
            # For SwissBilling: if the SO is not done yet, cancel directly.
            # Otherwise, refund.
            if (order.qoqa_bind_ids and
                    order.payment_mode_id.payment_settlable_on_qoqa):
                cancel_direct = True
            # payment_ids = None
            invoices = self.env['account.invoice'].browse()
            # if cancel_direct:
            #     If the order can be canceled on QoQa, the payment is
            #     canceled as well on QoQa so the internal payments
            #     can just be withdrawn.
            #     Otherwise, we have to keep them, they will be
            #     reconciled with the invoice
            #     WARNING! Delete account.move,
            #     not just payments (account.move.line)

            #     TODO: not sure we'll still have order.payment_ids
            #     payment_moves = [payment.move_id
            #                      for payment
            #                      in order.payment_ids]
            #     for move in payment_moves:
            #         move.unlink()
            if not cancel_direct and order.amount_total:
                # create the invoice, open it because we need the move
                # lines so we'll be able to reconcile them with the
                # payments
                order.action_invoice_create(grouped=False)
                invoices = order.invoice_ids
                invoices.signal_workflow('invoice_open')
                for invoice in invoices:
                    # create a refund since the payment cannot be
                    # canceled
                    actions = self._refund_all_invoices()

                # We can't cancel an order with open invoices, but
                # we still want to do that, because we need the move lines
                # to be there to reconcile them with the payments. The
                # sales order is really canceled though. So we disconnect the
                # invoices then link them again after the cancellation.
                # We have the same issue with the automatic payments so
                # we use the same trick

                # TODO: see if we get rid of order.payment_ids or not
                # payments = order.payment_ids
                # payment_ids = [payment.id for payment in payments]
                # payment_commands = [(3, pay_id) for pay_id in payment_ids]

                invoice_commands = [(3, inv.id) for inv in invoices]
                # order.write({'payment_ids': payment_commands,
                #              'invoice_ids': invoice_commands})
                order.write({'invoice_ids': invoice_commands})

            # cancel the pickings
            for picking in order.picking_ids:
                # draft pickings are already canceled by the cancellation
                # of the sale order so we don't need to take care of
                # them.
                if picking.state not in ('draft', 'cancel', 'done'):
                    picking.action_cancel()

            # cancel the invoices
            for invoice in invoices:
                # paid invoices were set as opened due to payments
                # being deleted, or were "detached" previously since
                # they will be refunded. Draft invoices will be cancelled
                # by the sale order cancellation.
                if invoice.state not in ('draft', 'cancel', 'paid'):
                    invoice.signal_workflow('invoice_cancel')

            super(SaleOrder, order).action_cancel()
            # if invoices or payment_ids:
            if invoices:
                # TODO: see if we get rid of payments or not
                # payment_commands = [(4, pay_id) for pay_id in payment_ids]
                invoice_commands = [(4, inv.id) for inv in invoices]
                # order.write({'payment_ids': payment_commands,
                #              'invoice_ids': invoice_commands})
                order.write({'invoice_ids': invoice_commands})

        action_res = None
        if actions:
            action_res = self.action_res = self._parse_refund_action(actions)

        self._call_cancel(cancel_direct=cancel_direct)

        if action_res:
            return action_res

        return True

    @api.multi
    def action_done(self):
        res = super(SaleOrder, self).action_done()
        # Browse orders to send 'settled' to BO
        for order in self:
            if (order.qoqa_bind_ids and
                    order.payment_mode_id.payment_settlable_on_qoqa):
                session = ConnectorSession.from_env(self.env)
                for binding in order.qoqa_bind_ids:
                    _logger.info("Settle order %s later (job) on QoQa",
                                 binding.name)
                    settle_sales_order.delay(session, binding._model._name,
                                             binding.id, priority=1)
        return res

    # TODO: still needed?
    @api.multi
    def action_force_cancel(self):
        """ Force cancellation of a done sales order.

        Only usable on done sales orders (so in the final state of the
        workflow) to avoid to break the workflow in the middle of its
        course.
        At QoQa, they might deliver sales orders and only cancel the order
        afterwards. In that case, even if the sales order is done, they need
        to set it as canceled on OpenERP and on the backend.
        """
        actions = []
        for sale in self:
            if sale.state != 'done':
                raise exceptions.UserError(
                    _('Only done sales orders can be forced to be canceled.')
                )

            sale.order_line.write({'state': 'cancel'})

            cancel_direct = False
            if (sale.qoqa_bind_ids and
                    sale.payment_mode_id.payment_cancellable_on_qoqa and
                    not sale.payment_mode_id.payment_settlable_on_qoqa):
                binding = sale.qoqa_bind_ids[0]
                # can be canceled only the day of the payment
                payment_date = fields.Date.from_string(
                    binding.qoqa_payment_date
                )
                if payment_date == date.today():
                    cancel_direct = True
            if cancel_direct:
                # Done the same day; remove payments
                # TODO: not sure we'll still have order.payment_ids
                # payment_moves = [payment.move_id
                #                  for payment
                #                  in sale.payment_ids]
                # for move in payment_moves:
                #     move.unlink()
                # Cancel now-reopened invoices
                for invoice in sale.invoice_ids:
                    invoice.signal_workflow('invoice_cancel')
            else:
                actions = self._refund_all_invoices()

        self.write({'state': 'cancel'})
        message = _("The sales order was done, but it has been manually "
                    "canceled.")
        self.message_post(body=message)

        # Return view for refunds
        action_res = None
        if actions:
            action_res = self.action_res = self._parse_refund_action(actions)

        self._call_cancel(cancel_direct=cancel_direct)

        if action_res:
            return action_res

        return True

    def _refund_all_invoices(self):
        refund_model = self.env['account.invoice.refund']
        actions = []
        for order in self:
            for invoice in order.invoice_ids:
                # create a refund since the payment cannot be
                # canceled
                action = refund_model.with_context(
                    active_model='account.invoice',
                    active_id=invoice.id,
                    active_ids=invoice.ids,
                ).create(
                    {'filter_refund': 'refund',
                     'description': _('Order Cancellation')}
                ).invoice_refund()

                actions.append(action)
        return actions

    def _parse_refund_action(self, actions):
        # Prepare the returning action.
        # Done before we call the cancellation on QoQa so if
        # something fails here, we won't call the QoQa API
        action_res = actions[0]
        refund_ids = []
        for action in actions:
            for field, op, value in action_res['domain']:
                if field == 'id' and op == 'in':
                    refund_ids += value
        if len(refund_ids) == 1:
            # remove the domain, replaced by res_id
            # the refund will be open in the form view
            action_res['domain'] = False
            action_res['res_id'] = refund_ids[0]
            view = self.env.ref('account.invoice_form')
            action_res['views'] = [(view.id, 'form')]
        else:
            # open as tree view, merge all the ids of the refunds
            # in the domain
            new_domain = []
            for field, op, value in action_res['domain']:
                if field == 'id' and op == 'in':
                    new_domain.append((field, op, refund_ids))
                else:
                    new_domain.append((field, op, value))
            action_res['domain'] = new_domain
        return action_res


@qoqa
class QoQaSaleOrderAdapter(QoQaAdapter):
    _model_name = 'qoqa.sale.order'
    _endpoint = 'admin/orders'
    _resource = 'order'

    def cancel(self, id):
        url = self.url()
        response = self.client.put(url + str(id) + '/cancel',
                                   data=json.dumps({'cancelled': True}))
        self._handle_response(response)

    def create_payment(self, id, amount, kind):
        """ Create a payment on the order

        ``kind`` can be a value of:
          - standard
          - credit_note
          - unclaimed
        """
        assert kind in ('standard', 'credit_note', 'unclaimed')
        url = '%s%s/payments' % (self.url(), id)

        payload = {
            'payment': {
                'amount': str(amount),
                'kind': kind,
            }
        }
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        response = self.client.post(url,
                                    data=json.dumps(payload),
                                    headers=headers)
        return self._handle_response(response)

    def add_trackings(self, id, packages):
        """ Synchronize picking packages.
        """
        url = "%s%s/shipping_packages" % (self.url(), id)

        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        response = self.client.post(url,
                                    data=json.dumps(packages),
                                    headers=headers)
        self._handle_response(response)


@qoqa
class QoQaPaymentAdapter(QoQaAdapter):
    _model_name = 'qoqa.payment'  # virtual model
    _endpoint = 'admin/payments'
    _resource = 'payment'

    def settle(self, id):
        url = "{}{}/settle".format(self.url(), id)
        response = self.client.post(url)
        self._handle_response(response)

    def refund(self, id, amount):
        """ Create a credit note on the QoQa backend, return the payment id """
        url = "{}{}/credit_notes".format(self.url(), id)
        response = self.client.post(url, data=json.dumps({'amount': amount}))
        return self._handle_response(response)
