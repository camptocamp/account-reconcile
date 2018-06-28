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
from .exporter import disable_shipping_address_modification as disable


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
        context={'active_test': False},
    )
    active = fields.Boolean(string='Active', default=True)
    amount_total_without_voucher = fields.Monetary(
        string='Total without Voucher',
        store=False,
        readonly=True,
        compute='_compute_amount_total_without_voucher',
    )

    def create_disable_address_change_job(self):
        binding_ids = self.mapped('qoqa_bind_ids').ids
        session = ConnectorSession.from_env(self.env)
        _logger.info("Disable shipping address change on "
                     "orders %s later (job) on QoQa",
                     binding_ids)
        if binding_ids:
            disable.delay(session, 'qoqa.sale.order', binding_ids, priority=1)

    @api.depends('order_line.price_total', 'order_line.is_voucher')
    def _compute_amount_total_without_voucher(self):
        for record in self:
            voucher_total = 0.
            for line in record.order_line:
                if not line.is_voucher:
                    continue
                # We don't have taxes on the vouchers, so we don't care
                # about them
                voucher_total += line.price_subtotal
            total = record.amount_total - voucher_total
            # We use this amount to check if we have the same total on the
            # QoQa4 website and in Odoo. On their side, they don't have the
            # negative lines for the voucher and we do.
            # Used for the sales exception.
            record.amount_total_without_voucher = total

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
    def _call_cancel(self):
        """ Synchronus cancel call on sale orders

        Only cancel on qoqa if all the cancellations succeeded
        canceled_in_backend means already canceled on QoQa.

        Should be called at the very end of the 'cancel' method so we
        won't call 'cancel' on qoqa if something failed before
        """
        self.ensure_one()
        if not self.canceled_in_backend:
            session = ConnectorSession.from_env(self.env)
            for binding in self.qoqa_bind_ids:
                # we want to do a direct call to the API so we validate that
                # the order could well be cancelled on Qoqa before commiting
                # the change in Odoo
                _logger.info("Cancel order %s directly on QoQa",
                             binding.name)
                message = _('Impossible to cancel the sales order '
                            'on the backend now.')
                with api_handle_errors(message):
                    cancel_sales_order(session, binding._model._name,
                                       binding.id)

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
            delivered = order.picking_ids.filtered(lambda r: r.state == 'done')
            all_service = all(line.product_id.type == 'service'
                              for line in order.order_line)
            payment_cancellable = False
            if (order.qoqa_bind_ids and
                    order.payment_mode_id.payment_cancellable_on_qoqa):
                binding = order.qoqa_bind_ids[0]
                # can be canceled only the day of the payment
                payment_date = fields.Date.from_string(
                    binding.qoqa_payment_date
                )
                if payment_date == date.today():
                    payment_cancellable = True

                if (not delivered and
                        order.payment_mode_id.payment_settlable_on_qoqa):
                    payment_cancellable = True
                if (all_service and
                        order.payment_mode_id.payment_settlable_on_qoqa):
                    if order.state != 'done':
                        payment_cancellable = True
                    else:
                        payment_cancellable = False

            existing_invoices = order.invoice_ids
            if not payment_cancellable and order.amount_total:
                # create the invoice, so we'll be able to create the refund
                # later, we'll cancel the invoice
                try:
                    order.action_invoice_create(grouped=False)
                except exceptions.UserError:
                    # the invoice already exists
                    pass
                invoices = order.invoice_ids.filtered(
                    lambda r: r.state != 'cancel'
                )
                invoices.signal_workflow('invoice_open')
                existing_invoices = order.invoice_ids
                # create a refund since the payment cannot be canceled
                actions += invoices._refund_and_get_action(
                    _('Order Cancellation')
                )

            if payment_cancellable:
                existing_invoices.filtered(
                    lambda r: r.state not in ('paid', 'cancel')
                ).signal_workflow('invoice_cancel')

            if not delivered:
                order.picking_ids.action_cancel()

            super(SaleOrder, order).action_cancel()
            order._call_cancel()

        if actions:
            action_res = self._parse_refund_action(actions)
            return action_res

        return True

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

    @api.multi
    def can_change_shipping_address(self):
        """Hook on checking the shipping address.
        """
        self.ensure_one()
        # no address switcherooni after pickings are added to batch
        return self._can_be_changed_by_eshop()

    @api.multi
    def can_change_shipping_date(self):
        """Hook on checking the shipping date.
        """
        self.ensure_one()
        # no date switcherooni after pickings are added to batch
        return self._can_be_changed_by_eshop()

    @api.multi
    def _can_be_changed_by_eshop(self):
        """Check if sale.order is available for change.
        """
        if self.picking_ids.mapped('batch_picking_id'):
            return False
        else:
            for picking in self.picking_ids:
                try:
                    picking.sudo()._check_existing_shipping_label()
                except exceptions.UserError:
                    return False
            return True

    @api.multi
    def _change_shipping_address(self, address):
        """ Change shipping address for the sale order.

        :param address: res.partner recordset with one value
        """
        self.ensure_one()
        self.partner_shipping_id = address
        if self.picking_ids:
            self.picking_ids.write({
                'partner_id': address.id,
            })
        return True

    @api.multi
    def _change_shipping_date(self, shipping_date):
        """Change shipping date of the sale order.

        :param shipping_date: string of YY-MM-DD hh:mm:ss format"""
        self.ensure_one()
        if self.picking_ids:
            self.picking_ids.write({
                'min_date': shipping_date,
                'picking_type_id':
                'connector_qoqa.picking_type_postpone_delivery',
            })
        return True


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

    def create_payment(self, id, amount, kind, refno):
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
                'refno': refno,
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

    def disable_shipping_address_modification(self, sale_orders):
        """ Disable changing of shipping address on qoqa SO

        :param sale_orders: list of ids
        """
        url = '%sdisable_modification' % (self.url(), )
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        payload = {
            'order_ids': sale_orders,
        }
        response = self.client.put(url,
                                   data=json.dumps(payload),
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
