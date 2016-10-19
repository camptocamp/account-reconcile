# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import division

import logging

from dateutil import parser

from openerp import fields, _
from openerp.tools.float_utils import float_is_zero

from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  ImportMapper,
                                                  )
from openerp.addons.connector.exception import FailedJobError
from openerp.addons.connector_ecommerce.unit.sale_order_onchange import (
    SaleOrderOnChange)
from ..backend import qoqa
from ..exception import QoQaError
from ..unit.importer import DelayedBatchImporter, QoQaImporter
from ..unit.mapper import (iso8601_to_utc,
                           iso8601_local_date,
                           FromDataAttributes,
                           backend_to_m2o,
                           )
from ..connector import iso8601_to_local_date

_logger = logging.getLogger(__name__)


class QoQaOrderStatus(object):
    paid = 'paid'
    cancelled = 'cancelled'
    # other status should never be given by the API


class QoQaInvoiceStatus(object):
    requested = 'requested'
    confirmed = 'confirmed'
    cancelled = 'cancelled'


class QoQaInvoiceKind(object):
    invoice = 'standard'
    credit_note = 'credit_note'


class QoQaPaymentStatus(object):
    success = 'success'
    requested = 'requested'
    confirmed = 'confirmed'
    cancelled = 'cancelled'
    failed = 'failed'


class QoQaPaymentKind(object):
    payment = 'standard'
    credit_note = 'credit_note'


DAYS_BEFORE_CANCEL = 30


@qoqa
class SaleOrderBatchImport(DelayedBatchImporter):
    """ Import the QoQa Sales Order.

    For every sales order's id in the list, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.sale.order'


@qoqa
class SaleOrderImporter(QoQaImporter):
    _model_name = 'qoqa.sale.order'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        data = self.qoqa_record['data']
        attrs = data['attributes']
        rels = data['relationships']
        self._import_dependency(attrs['website_id'], 'qoqa.shop')
        self._import_dependency(attrs['offer_id'], 'qoqa.offer')
        self._import_dependency(attrs['shipping_fee_id'], 'qoqa.shipping.fee')
        self._import_dependency(rels['user']['data']['id'], 'qoqa.res.partner')
        self._import_dependency(rels['billing_address']['data']['id'],
                                'qoqa.address', always=True)
        self._import_dependency(rels['shipping_address']['data']['id'],
                                'qoqa.address', always=True)

    def must_skip(self):
        """ Returns a reason if the import should be skipped.

        Returns None to continue with the import

        """
        attrs = self.qoqa_record['data']['attributes']
        if attrs['status'] == QoQaOrderStatus.cancelled:
            sale = self.binder.to_openerp(self.qoqa_id, unwrap=True)
            if not sale:
                # do not import the canceled sales orders if they
                # have not been already imported
                return _('Sales order %s is not imported because it '
                         'has been canceled.') % self.qoqa_record['data']['id']
            else:
                # Already imported orders, but canceled afterwards,
                # triggers the automatic cancellation
                if sale.state != 'cancel' and not sale.canceled_in_backend:
                    sale.write({'canceled_in_backend': True})
                    return (_('Sales order %s has been marked '
                              'as "to cancel".') %
                            self.qoqa_record['data']['id'])

    def _is_uptodate(self, binding):
        """ Check whether the current sale order should be imported or not.

        States on QoQa are:

        * paid: authorized on datatrans, not captured
        * cancelled: final state for cancellations
        * the other states are never given to us through the API

        How we will handle them:

        paid
            They will be confirmed as soon as they are imported (excepted
            if they have 'sales exceptions').

        cancelled
            If the sales order has never been imported before, we skip it.
            If it has been cancelled after being confirmed and imported,
            it will try to cancel it in Odoo, or if it can't, it will
            active the 'need_cancel' fields and log a message (featured
            by `connector_ecommerce`.

        """
        # already imported, skip it
        assert self.qoqa_record
        if self.binder.to_openerp(self.qoqa_id):
            return True
        # when the offer is empty, this is a B2B / manual invoice
        # we don't want to import them
        if not self.qoqa_record['data']['attributes']['offer_id']:
            return True

    def _import(self, binding_id):
        qshop_binder = self.binder_for('qoqa.shop')
        website_id = self.qoqa_record['data']['attributes']['website_id']
        shop_binding = qshop_binder.to_openerp(website_id)
        user = shop_binding.company_id.connector_user_id
        user = self.env.ref('connector_qoqa.user_connector_ch')
        if not user:
            raise QoQaError('No connector user configured for company %s' %
                            shop_binding.company_id.name)
        with self.session.change_user(user.id):
            super(SaleOrderImporter, self)._import(binding_id)


def get_payments(connector_unit, record):
    payments = [item for item in
                record['included']
                if item['type'] == 'payment' and
                item['attributes']['kind'] == QoQaPaymentKind.payment
                ]
    return payments


def _get_payment_mode(connector_unit, payment, company):
    valid_states = (QoQaPaymentStatus.success,
                    QoQaPaymentStatus.confirmed)
    if payment['attributes']['status'] not in valid_states:
        return
    qmethod_id = payment['attributes']['payment_method_id']
    if not qmethod_id:
        raise MappingError("Payment method missing for payment %s" %
                           payment['id'])
    binder = connector_unit.binder_for('account.payment.mode')
    method = binder.to_openerp(qmethod_id, company_id=company.id)
    if not method:
        raise FailedJobError(
            "The configuration is missing for the Payment "
            "Mode with ID '%s'.\n\n"
            "Resolution:\n"
            "- Go to "
            "'Invoicing > Configuration > Management > Payment Modes\n"
            "- Create a new Payment Mode with qoqa_id '%s'\n"
            "- Optionally link the Payment Mode to an existing "
            "Automatic Workflow Process or create a new one." %
            (qmethod_id, qmethod_id))
    return method


def _get_payment_date(payment_record):
    payment_date = payment_record['attributes']['created_at']
    payment_date = iso8601_to_local_date(payment_date)
    return fields.Date.to_string(payment_date)


def valid_invoices(sale_record):
    """ Extract all invoices from a sales order having a valid status
    and of type 'invoice' (not refunds).

    Return a list of valid invoices

    """
    valid_status = (QoQaInvoiceStatus.confirmed)
    invoices = [item for item in sale_record['included']
                if item['type'] == 'invoice' and
                item['attributes']['status'] in valid_status and
                item['attributes']['kind'] == QoQaInvoiceKind.invoice]
    return invoices


def find_sale_invoice(invoices):
    """ Find and return the invoice used for the sale from the invoices.

    Several invoices can be there, but only 1 is the invoice that
    interest us. (others are refund, ...)

    We use it to have the price of the products, shipping fees, discounts
    and the grand total.

    """
    if not invoices:
        raise MappingError('1 invoice expected, got no invoice')
    if len(invoices) == 1:
        return invoices[0]

    def sort_key(invoice):
        dt_str = invoice['attributes']['created_at']
        return parser.parse(dt_str)

    # when we have several invoices, find the last one, the first
    # has probably been reverted by a refund
    invoices = sorted(invoices, key=sort_key, reverse=True)
    return invoices[0]


@qoqa
class SaleOrderImportMapper(ImportMapper, FromDataAttributes):
    _model_name = 'qoqa.sale.order'

    from_data_attributes = [
        (iso8601_to_utc('created_at'), 'created_at'),
        (iso8601_local_date('created_at'), 'date_order'),
        (iso8601_to_utc('updated_at'), 'updated_at'),
        (backend_to_m2o('website_id'), 'qoqa_shop_id'),
        (backend_to_m2o('offer_id'), 'offer_id'),
    ]

    @mapping
    def name(self, record):
        order_id = record['data']['id']
        return {'name': order_id.zfill(8)}

    @mapping
    def addresses(self, record):
        rels = record['data']['relationships']
        quser_id = rels['user']['data']['id']
        binder = self.binder_for('qoqa.res.partner')
        partner = binder.to_openerp(quser_id, unwrap=True)

        values = {'partner_id': partner.id}

        binder = self.binder_for('qoqa.address')
        # in the old sales orders, addresses may be missing, in such
        # case we set the partner_id
        qship_id = rels.get('shipping_address', {}).get('data', {}).get('id')
        if qship_id:
            shipping = binder.to_openerp(qship_id, unwrap=True)
            values['partner_shipping_id'] = shipping.id
        qbill_id = rels.get('billing_address', {}).get('data', {}).get('id')
        if qbill_id:
            billing = binder.to_openerp(qbill_id, unwrap=True)
            values['partner_invoice_id'] = billing.id
        return values

    @mapping
    def payment_mode(self, record):
        # Retrieve methods, to ensure that we don't have
        # only cancelled payments
        qoqa_shop_binder = self.binder_for('qoqa.shop')
        website_id = record['data']['attributes']['website_id']
        qoqa_shop = qoqa_shop_binder.to_openerp(website_id)
        company = qoqa_shop.company_id

        qpayments = get_payments(self, record)
        methods = ((payment,
                    _get_payment_mode(self, payment, company))
                   for payment in qpayments)

        methods = (method for method in methods if method[1])
        methods = sorted(methods, key=lambda m: m[1].sequence)
        if not methods:
            # a sales order may not have a payment method because the
            # customer didn't need to pay: it has a discount as high as
            # the total. In that case, we force an automatic workflow
            total = float(record['data']['attributes']['total'])
            if float_is_zero(total, precision_digits=2):
                xmlid = 'sale_automatic_workflow.automatic_validation'
                try:
                    auto_wkf = self.env.ref(xmlid)
                except ValueError:
                    raise MappingError('Can not find the automatic sale '
                                       'workflow with (xmlid: %s)' % xmlid)
                return {'workflow_process_id': auto_wkf.id}
            return
        method = methods[0]
        payment_attrs = method[0]['attributes']
        transaction_id = payment_attrs['transaction_id']
        payment_amount = payment_attrs['amount']
        payment_date = _get_payment_date(method[0])
        return {'payment_mode_id': method[1].id,
                'qoqa_transaction': transaction_id,
                # keep as payment's reference
                'qoqa_payment_id': method[0]['id'],
                'qoqa_payment_date': payment_date,
                'qoqa_payment_amount': payment_amount,
                # used for the reconciliation (transfered to invoice)
                'transaction_id': method[0]['id']}

    @mapping
    def total(self, record):
        attrs = record['data']['attributes']
        values = {'qoqa_amount_total': attrs['total']}
        return values

    @mapping
    def reference(self, record):
        attrs = record['data']['attributes']
        values = {'client_order_ref': attrs['reference']}
        return values

    @mapping
    def from_invoice(self, record):
        """ Get the invoice node and extract some data """
        invoices = valid_invoices(record)
        invoice = find_sale_invoice(invoices)
        return {'invoice_ref': invoice['attributes']['reference']}

    def finalize(self, map_record, values):
        lines = self.extract_lines(map_record)
        map_child = self.unit_for(self._map_child_class,
                                  'qoqa.sale.order.line')
        items = map_child.get_items(lines, map_record,
                                    'qoqa_order_line_ids',
                                    options=self.options)
        values['qoqa_order_line_ids'] = items

        onchange = self.unit_for(SaleOrderOnChange)
        return onchange.play(values, values['qoqa_order_line_ids'])

    def extract_lines(self, map_record):
        """ Lines are read in the invoice of the sales order """
        invoice = find_sale_invoice(valid_invoices(map_record.source))
        line_ids = [item['id'] for item
                    in invoice['relationships']['invoice_items']['data']
                    ]
        lines = [item for item in map_record.source['included']
                 if item['type'] == 'invoice_item' and
                 item['id'] in line_ids]
        return lines


@qoqa
class QoQaSaleOrderOnChange(SaleOrderOnChange):
    _model_name = 'qoqa.sale.order'

    order_onchange_fields = SaleOrderOnChange.order_onchange_fields + [
        'qoqa_shop_id',
    ]
