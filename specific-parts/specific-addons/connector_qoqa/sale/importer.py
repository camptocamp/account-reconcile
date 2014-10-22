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
from __future__ import division

import logging
from dateutil import parser

from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.float_utils import float_is_zero

from openerp.addons.connector.exception import MappingError
from openerp.addons.connector.unit.mapper import (mapping,
                                                  backend_to_m2o,
                                                  ImportMapper,
                                                  )
from openerp.addons.connector.exception import FailedJobError
from openerp.addons.connector_ecommerce.unit.sale_order_onchange import (
    SaleOrderOnChange)
from ..backend import qoqa
from ..unit.backend_adapter import QoQaAdapter
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        )
from ..unit.mapper import iso8601_to_utc, strformat, iso8601_local_date
from ..connector import (iso8601_to_local_date,
                         historic_import,
                         )
from ..exception import QoQaError
from ..sale_line.importer import (QOQA_ITEM_PRODUCT, QOQA_ITEM_SHIPPING,
                                  QOQA_ITEM_DISCOUNT, QOQA_ITEM_SERVICE,
                                  )

_logger = logging.getLogger(__name__)

# http://admin.test02.qoqa.com/orderStatus
QOQA_STATUS_REQUESTED = 1  # order is created
QOQA_STATUS_PAID = 2  # order is paid, not captured by Datatrans
QOQA_STATUS_CONFIRMED = 3  # order is paid, payment confirmed
QOQA_STATUS_CANCELLED = 4  # order is canceled
QOQA_STATUS_PROCESSED = 5  # order is closed, delivered
# http://admin.test02.qoqa.com/paymentStatus
QOQA_PAY_STATUS_CONFIRMED = 5
QOQA_PAY_STATUS_SUCCESS = 2
QOQA_PAY_STATUS_ACCOUNTED = 7
QOQA_PAY_STATUS_ABORT = 4
QOQA_PAY_STATUS_FAILED = 3
QOQA_PAY_STATUS_CANCELLED = 6
QOQA_PAY_STATUS_PENDING = 1
# http://admin.test02.qoqa.com/invoiceType
QOQA_INVOICE_TYPE_ISSUED = 1
QOQA_INVOICE_TYPE_RECEIVED = 2
QOQA_INVOICE_TYPE_ISSUED_CN = 3
QOQA_INVOICE_TYPE_RECEIVED_CN = 4
# http://admin.test02.qoqa.com/invoiceStatus
QOQA_INVOICE_STATUS_REQUESTED = 1
QOQA_INVOICE_STATUS_CONFIRMED = 2
QOQA_INVOICE_STATUS_CANCELLED = 3
QOQA_INVOICE_STATUS_ACCOUNTED = 4

DAYS_BEFORE_CANCEL = 30


@qoqa
class SaleOrderBatchImport(DelayedBatchImport):
    """ Import the QoQa Sales Order.

    For every sales order's id in the list, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.sale.order'


@qoqa
class SaleOrderImport(QoQaImportSynchronizer):
    _model_name = 'qoqa.sale.order'

    def _import_dependencies(self):
        """ Import the dependencies for the record"""
        assert self.qoqa_record
        rec = self.qoqa_record
        self._import_dependency(rec['shop_id'], 'qoqa.shop')
        self._import_dependency(rec['deal_id'], 'qoqa.offer')
        self._import_dependency(rec['user_id'], 'qoqa.res.partner',
                                always=True)
        self._import_dependency(rec['billing_address_id'],
                                'qoqa.address', always=True)
        self._import_dependency(rec['shipping_address_id'],
                                'qoqa.address', always=True)
        for item in rec['items']:
            self._import_dependency(item['variation_id'],
                                    'qoqa.product.product')
            self._import_dependency(item['offer_id'],
                                    'qoqa.offer.position')

    def must_skip(self):
        """ Returns a reason if the import should be skipped.

        Returns None to continue with the import

        """
        if self.qoqa_record['status_id'] == QOQA_STATUS_CANCELLED:
            sale_id = self.binder.to_openerp(self.qoqa_id, unwrap=True)
            if sale_id is None:
                # do not import the canceled sales orders if they
                # have not been already imported
                return _('Sales order %s is not imported because it '
                         'has been canceled.') % self.qoqa_record['id']
            else:
                # Already imported orders, but canceled afterwards,
                # triggers the automatic cancellation
                sale = self.session.browse('sale.order', sale_id)
                if sale.state != 'cancel' and not sale.canceled_in_backend:
                    self.session.write('sale.order', [sale_id],
                                       {'canceled_in_backend': True})
                    return _('Sales order %s has been marked '
                             'as "to cancel".') % self.qoqa_record['id']

    def _is_uptodate(self, binding_id):
        """ Check whether the current sale order should be imported or not.

        States or QoQa are:

        * requested: an order has been created
        * paid: authorized on datatrans, not captured
        * confirmed: payment has been confirmed / captured by datatrans
        * processed: final state, when is order is delivered
        * cancelled: final state for cancellations

        The API only gives us the "confirmed" and "processed" sales orders.

        How we will handle them:

        requested, paid
            Not given by the API

        confirmed
            They will be confirmed as soon as they are imported (excepted
            if they have 'sales exceptions').

        processed
            We will short-circuit the workflow and set them directly to
            'done'. They are imported for the history.

        cancelled
            If the sales order has never been imported before, we skip it.
            If it has been cancelled after being confirmed and imported,
            it will try to cancel it in OpenERP, or if it can't, it will
            active the 'need_cancel' fields and log a message (featured
            by `connector_ecommerce`.

        """
        # already imported, skip it (unless if `force` is used)
        assert self.qoqa_record
        if self.binder.to_openerp(self.qoqa_id) is not None:
            return True
        # when the deal is empty, the this is a B2B / manual invoice
        # we don't want to import them
        if not self.qoqa_record['deal_id']:
            return True

    def _import(self, binding_id):
        qshop_binder = self.get_binder_for_model('qoqa.shop')
        qshop_id = qshop_binder.to_openerp(self.qoqa_record['shop_id'])
        qshop = self.session.browse('qoqa.shop', qshop_id)
        user = qshop.company_id.connector_user_id
        if not user:
            raise QoQaError('No connector user configured for company %s' %
                            qshop.company_id.name)
        with self.session.change_user(user.id):
            super(SaleOrderImport, self)._import(binding_id)

    def _create_payments(self, binding_id):
        sess = self.session
        sale_obj = sess.pool['sale.order']
        qsale = sess.browse(self.model._name, binding_id)
        sale = qsale.openerp_id
        if sale.payment_ids:
            # if payments exist, we are force updating a sales
            # and the payments have already been generated
            return
        for payment in self.qoqa_record['payments']:
            method = _get_payment_method(self, payment, sale.company_id.id)
            if method is None:
                continue
            journal = method.journal_id
            if not journal:
                continue
            amount = payment['amount'] / 100
            payment_date = _get_payment_date(payment)
            cr, uid, context = sess.cr, sess.uid, sess.context
            sale_obj._add_payment(cr, uid, sale, journal,
                                  amount, payment_date, context=context)

    def _after_import(self, binding_id):
        # before 'date_really_import', we import only for the historic
        # so we do not want to generate payments, invoice, stock moves
        historic_info = historic_import(self, self.qoqa_record)
        if historic_info.historic:
            # no invoice, no packing, no payment
            sess = self.session
            sale = sess.browse('qoqa.sale.order', binding_id)
            # check if the amounts do not match, only for historic
            # imports, this check is done with sale exceptions otherwise
            if abs(sale.amount_total - sale.qoqa_amount_total) >= 0.01:
                raise MappingError('Amounts do not match. Expected: %0.2f, '
                                   'got: %0.2f' %
                                   (sale.qoqa_amount_total, sale.amount_total))

            # generate an invoice so we will be able to create
            # merchandise returns based on the invoice
            # the invoice workflow is short-circuited too, we don't
            # want move lines
            if not sale.invoice_ids:
                # if we force update, do not generate again the invoice
                invoice_id = sale.openerp_id.action_invoice_create(
                    grouped=False, states=['draft'],
                    date_invoice=sale.date_order)
                sess.pool['account.invoice'].confirm_paid(sess.cr, sess.uid,
                                                          [invoice_id],
                                                          context=sess.context)
                if not historic_info.active:
                    # hide old invoices (more than 2 years)
                    sess.write('account.invoice', [invoice_id],
                               {'active': False})

            sale.openerp_id.action_done()
            _logger.debug('Sales order %s is processed, workflow '
                          'short-circuited in OpenERP', sale.name)
        else:
            self._create_payments(binding_id)


def _get_payment_method(connector_unit, payment, company_id):
    session = connector_unit.session
    valid_states = (QOQA_PAY_STATUS_CONFIRMED,
                    QOQA_PAY_STATUS_SUCCESS,
                    QOQA_PAY_STATUS_ACCOUNTED)
    if payment['status_id'] not in valid_states:
        return
    qmethod_id = payment['method_id']
    if qmethod_id is None:
        raise MappingError("Payment method missing for payment %s" %
                           payment['id'])
    binder = connector_unit.get_binder_for_model('payment.method')
    method_id = binder.to_openerp(qmethod_id, company_id=company_id)
    if not method_id:
        raise FailedJobError(
            "The configuration is missing for the Payment "
            "Method with ID '%s'.\n\n"
            "Resolution:\n"
            "- Go to "
            "'Sales > Configuration > Sales > Customer Payment Method\n"
            "- Create a new Payment Method with qoqa_id '%s'\n"
            "-Eventually  link the Payment Method to an existing Workflow "
            "Process or create a new one." % (qmethod_id, qmethod_id))
    return session.browse('payment.method', method_id)


def _get_payment_date(payment_record):
    payment_date = (payment_record['trx_date'] or
                    payment_record['created_at'])
    payment_date = iso8601_to_local_date(payment_date)
    date_fmt = DEFAULT_SERVER_DATE_FORMAT
    return payment_date.strftime(date_fmt)


def valid_invoices(sale_record):
    """ Extract all invoices from a sales order having a valid status
    and of type 'invoice' (not refunds).

    Return a generator with the valid invoices

    """
    invoices = sale_record['invoices']
    invoices = [inv for inv in invoices if
                inv['type_id'] == QOQA_INVOICE_TYPE_ISSUED and
                inv['status_id'] in (QOQA_INVOICE_STATUS_CONFIRMED,
                                     QOQA_INVOICE_STATUS_ACCOUNTED)]
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
        dt_str = invoice['created_at']
        return parser.parse(dt_str)

    # when we have several invoices, find the last one, the first
    # has probably been reverted by a refund
    invoices = sorted(invoices, key=sort_key, reverse=True)
    return invoices[0]


@qoqa
class SaleOrderImportMapper(ImportMapper):
    _model_name = 'qoqa.sale.order'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_local_date('created_at'), 'date_order'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              (backend_to_m2o('shop_id'), 'qoqa_shop_id'),
              (backend_to_m2o('shop_id', binding='qoqa.shop'), 'shop_id'),
              (strformat('id', '{0:08d}'), 'name'),
              (backend_to_m2o('shipper_service_id',
                              binding='qoqa.shipper.service'), 'carrier_id'),
              ]

    @mapping
    def active(self, record):
        historic_info = historic_import(self, record)
        if not historic_info.active:
            return {'active': False}

    @mapping
    def addresses(self, record):
        quser_id = record['user_id']
        binder = self.get_binder_for_model('qoqa.res.partner')
        partner_id = binder.to_openerp(quser_id, unwrap=True)

        binder = self.get_binder_for_model('qoqa.address')
        # in the old sales orders, addresses may be missing, in such
        # case we set the partner_id
        qship_id = record['shipping_address_id']
        shipping_id = (binder.to_openerp(qship_id, unwrap=True) if qship_id
                       else partner_id)
        qbill_id = record['billing_address_id']
        billing_id = (binder.to_openerp(qbill_id, unwrap=True) if qbill_id
                      else partner_id)
        values = {'partner_id': partner_id,
                  'partner_shipping_id': shipping_id,
                  'partner_invoice_id': billing_id}
        return values

    @mapping
    def payment_method(self, record):
        # Retrieve methods, to ensure that we don't have
        # only cancelled payments
        qpayments = record['payments']
        qshop_binder = self.get_binder_for_model('qoqa.shop')
        qshop_id = qshop_binder.to_openerp(record['shop_id'])
        qshop = self.session.read('qoqa.shop', qshop_id, ['company_id'])
        company_id = qshop['company_id'][0]
        try:
            methods = ((payment,
                        _get_payment_method(self, payment, company_id))
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
            # a sales order may not have a payment method because the
            # customer didn't need to pay: it has a discount as high as
            # the total. In that case, we force an automatic workflow
            invoices = valid_invoices(record)
            invoice = find_sale_invoice(invoices)
            if float_is_zero(invoice['total'] / 100, precision_digits=2):
                data_obj = self.session.pool['ir.model.data']
                xmlid = ('sale_automatic_workflow', 'automatic_validation')
                cr, uid = self.session.cr, self.session.uid
                try:
                    __, wkf_id = data_obj.get_object_reference(cr, uid, *xmlid)
                except ValueError:
                    raise MappingError('Can not find the sale workflow with '
                                       'XML ID %s.%s' % (xmlid[0], xmlid[1]))
                return {'workflow_process_id': wkf_id}
            return
        method = methods[0]
        transaction_id = method[0].get('transaction')
        payment_date = _get_payment_date(method[0])
        return {'payment_method_id': method[1].id,
                'qoqa_transaction': transaction_id,
                # keep as payment's reference
                'qoqa_payment_id': method[0]['id'],
                'qoqa_payment_date': payment_date,
                # used for the reconciliation (transfered to invoice)
                'transaction_id': method[0]['id']}

    @mapping
    def from_invoice(self, record):
        """ Get the invoice node and extract some data """
        invoices = valid_invoices(record)
        invoice = find_sale_invoice(invoices)
        total = float(invoice['total']) / 100
        # We can have several invoices, some are refunds, normally
        # we have only 1 invoice for sale.
        # Concatenate them, keep them in customer reference
        invoices_refs = ', '.join(inv['reference'] for inv in invoices)
        # keep the main one for copying in the invoice once generated
        ref = invoice['reference']
        values = {'qoqa_amount_total': total,
                  'invoice_ref': ref,
                  'client_order_ref': invoices_refs,
                  }
        return values

    @mapping
    def from_offer(self, record):
        """ Get the linked offer and takes some values from there """
        binder = self.get_binder_for_model('qoqa.offer')
        offer_id = binder.to_openerp(record['deal_id'], unwrap=True)
        offer = self.session.browse('qoqa.offer', offer_id)
        # the delivery method comes from the deal
        # (the 'shipper_service_id' in the record is not the carrier)
        values = {
            'offer_id': offer.id,
            'pricelist_id': offer.pricelist_id.id,
        }
        return values

    def finalize(self, map_record, values):
        lines = self.extract_lines(map_record)

        map_child = self.get_connector_unit_for_model(
            self._map_child_class, 'qoqa.sale.order.line')
        items = map_child.get_items(lines, map_record,
                                    'qoqa_order_line_ids',
                                    options=self.options)
        values['qoqa_order_line_ids'] = items

        onchange = self.get_connector_unit_for_model(SaleOrderOnChange)
        # date is required to apply the fiscal position rules
        with self.session.change_context({'date': values['date_order']}):
            return onchange.play(values, values['qoqa_order_line_ids'])

    def extract_lines(self, map_record):
        """ Lines are composed of 3 list of dicts. Extract lines.

        1 list is 'order_items', the other is 'items'. The third
        is in 'invoices'.
        We merge the 2 first dict, and we keep the invoice item
        in an 'invoice_item' key for the lines of the sales order.

        The invoice items are used to: get the amounts: add special lines
        like the shipping fees or discounts.

        The special lines are returned separately because they only have
        the invoice items, not the order items.

        """
        lines = []
        invoice = find_sale_invoice(valid_invoices(map_record.source))
        invoice_details = invoice['item_details']
        # used to check if lines have not been consumed
        details_by_id = dict((line['id'], line) for line
                             in invoice_details)
        lines = []
        for invoice_detail in invoice_details:
            detail_id = invoice_detail['id']
            item = invoice_detail['item']
            type_id = item['type_id']

            if type_id in (QOQA_ITEM_PRODUCT, QOQA_ITEM_SHIPPING):
                lines.append(details_by_id.pop(detail_id))

            elif type_id == QOQA_ITEM_DISCOUNT:
                adapter = self.get_connector_unit_for_model(QoQaAdapter,
                                                            'qoqa.promo')
                promo_values = adapter.read(item['promo_id'])
                line = details_by_id.pop(detail_id)
                line['promo'] = promo_values
                lines.append(line)

            elif type_id == QOQA_ITEM_SERVICE:
                raise MappingError("Items of type 'Service' are not "
                                   "supported.")

        if details_by_id:
            # an or several item(s) have not been handled
            raise MappingError('Remaining, unhandled, items in invoice: %s' %
                               details_by_id.values())
        return lines


@qoqa
class QoQaSaleOrderOnChange(SaleOrderOnChange):
    _model_name = 'qoqa.sale.order'

    def _play_line_onchange(self, line, previous_lines, order):
        new_line = super(QoQaSaleOrderOnChange, self)._play_line_onchange(
            line, previous_lines, order
        )
        if new_line.get('offer_position_id'):
            s = self.session
            sale_line_obj = s.pool['sale.order.line']
            # change the delay according to the offer position
            position_id = new_line['offer_position_id']
            res = sale_line_obj.onchange_offer_position_id(s.cr,
                                                           s.uid,
                                                           [],
                                                           position_id,
                                                           context=s.context)
            self.merge_values(new_line, res)
            # force override of 'delay' because merge_values only apply
            # undefined fields
            delay = res.get('value', {}).get('delay')
            if delay:
                new_line['delay'] = delay
        return new_line
