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
from datetime import datetime, timedelta
from operator import attrgetter

from openerp.tools.translate import _
from openerp.addons.connector.connector import ConnectorUnit
from openerp.addons.connector.unit.mapper import (mapping,
                                                  backend_to_m2o,
                                                  ImportMapper,
                                                  )
from openerp.addons.connector.exception import (NothingToDoJob,
                                                FailedJobError,
                                                )
from openerp.addons.connector_ecommerce.sale import ShippingLineBuilder
from openerp.addons.connector_ecommerce.unit.sale_order_onchange import (
    SaleOrderOnChange)
from ..backend import qoqa
from ..unit.import_synchronizer import (DelayedBatchImport,
                                        QoQaImportSynchronizer,
                                        )
from ..unit.mapper import iso8601_to_utc
from ..connector import iso8601_to_utc_datetime
from ..exception import OrderImportRuleRetry

_logger = logging.getLogger(__name__)

QOQA_STATUS_REQUESTED = 1  # order is created
QOQA_STATUS_PAID = 2  # order is paid, not captured by Datatrans
QOQA_STATUS_CONFIRMED = 3  # order is paid, payment confirmed
QOQA_STATUS_CANCELLED = 4  # order is canceled
QOQA_STATUS_PROCESSED = 5  # order is closed, delivered
QOQA_PAY_STATUS_CONFIRMED = 5
QOQA_PAY_STATUS_SUCCESS = 2
QOQA_PAY_STATUS_ACCOUNTED = 7
QOQA_PAY_STATUS_ABORT = 4
QOQA_PAY_STATUS_FAILED = 3
QOQA_PAY_STATUS_CANCELLED = 6
QOQA_PAY_STATUS_PENDING = 1
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
        self._import_dependency(rec['user_id'], 'qoqa.res.partner', always=True)
        self._import_dependency(rec['billing_address_id'],
                                'qoqa.address', always=True)
        self._import_dependency(rec['shipping_address_id'],
                                'qoqa.address', always=True)
        for item in rec['items']:
            self._import_dependency(item['variation_id'],
                                    'qoqa.product.product')
            self._import_dependency(item['offer_id'],
                                    'qoqa.offer.position')
            # TODO promo_id
            # self._import_dependency(item['promo_id'],
            #                         'qoqa.promo')
            # TODO
            # self._import_dependency(item['voucher_id'],
            #                         'qoqa.voucher')

    def must_skip(self):
        """ Returns a reason if the import should be skipped.

        Returns None to continue with the import

        """
        if self.qoqa_record['status_id'] == QOQA_STATUS_CANCELLED:
            return _('Sales order %s is not imported because it '
                     'has been canceled.') % self.qoqa_record['id']

    def _is_uptodate(self, binding_id):
        # already imported, skip it (unless if `force` is used)
        if self.binder.to_openerp(self.qoqa_id) is not None:
            return True

    def _before_import(self):
        rules = self.get_connector_unit_for_model(SaleImportRule)
        rules.check(self.qoqa_record)

    def _create_payments(self, binding_id):
        sess = self.session
        sale_obj = sess.pool['sale.order']
        qsale = sess.browse(self.model._name, binding_id)
        sale = qsale.openerp_id
        for payment in self.qoqa_record['payments']:
            valid_states = (QOQA_PAY_STATUS_CONFIRMED,
                            QOQA_PAY_STATUS_SUCCESS,
                            QOQA_PAY_STATUS_ACCOUNTED)
            if payment['status_id'] not in valid_states:
                continue
            method = _get_payment_method(self, payment, sale.company_id.id)
            journal = method.journal_id
            if not journal:
                continue
            amount = payment['amount'] / 100
            date = iso8601_to_utc_datetime(payment['trx_date'])
            cr, uid, context = sess.cr, sess.uid, sess.context
            sale_obj._add_payment(cr, uid, sale, journal,
                                  amount, date, context=context)

    def _after_import(self, binding_id):
        if self.qoqa_record['status_id'] == QOQA_STATUS_PROCESSED:
            # no invoice, no packing, no payment
            sess = self.session
            sale = sess.browse('qoqa.sale.order', binding_id).openerp_id
            sale.action_done()
            _logger.debug('QoQa Sales order %s is processed, workflow '
                          'short-circuited in OpenERP', self.qoqa_record['id'])
        else:
            self._create_payments(binding_id)


def _get_payment_method(connector_unit, payment, company_id):
    session = connector_unit.session
    qmethod_id = payment['method_id']
    binder = connector_unit.get_binder_for_model('payment.method')
    method_id = binder.to_openerp(qmethod_id, company_id=company_id)
    if not method_id:
        raise FailedJobError(
            "The configuration is missing for the Payment Method with ID '%s'.\n\n"
            "Resolution:\n"
            "- Go to 'Sales > Configuration > Sales > Customer Payment Method\n"
            "- Create a new Payment Method with qoqa_id '%s'\n"
            "-Eventually  link the Payment Method to an existing Workflow "
            "Process or create a new one." % (qmethod_id, qmethod_id))
    return session.browse('payment.method', method_id)


@qoqa
class SaleOrderImportMapper(ImportMapper):
    _model_name = 'qoqa.sale.order'

    direct = [(iso8601_to_utc('created_at'), 'created_at'),
              (iso8601_to_utc('updated_at'), 'updated_at'),
              (backend_to_m2o('shop_id'), 'qoqa_shop_id'),
              (backend_to_m2o('shop_id', binding='qoqa.shop'), 'shop_id'),
              (backend_to_m2o('user_id', binding='qoqa.res.partner'), 'partner_id'),
              (backend_to_m2o('shipping_address_id',
                              binding='qoqa.address'),
               'partner_shipping_id'),
              (backend_to_m2o('billing_address_id',
                              binding='qoqa.address'),
               'partner_invoice_id'),
              ('id', 'name'),
              ]

    @mapping
    def payment_method(self, record):
        qshop_binder = self.get_binder_for_model('qoqa.shop')
        qshop_id = qshop_binder.to_openerp(record['shop_id'])
        qshop = self.session.read('qoqa.shop', qshop_id, ['company_id'])
        company_id = qshop['company_id'][0]
        binder = self.get_binder_for_model('payment.method')
        payments = [_get_payment_method(self, payment, company_id)
                    for payment in record['payments']]
        payments = sorted(payments, key=attrgetter('sequence'))
        return {'payment_method_id': payments[0].id}

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
            'carrier_id': offer.carrier_id.id,
        }
        return values

    def _add_shipping_line(self, map_record, values):
        builder = self.get_connector_unit_for_model(QoQaShippingLineBuilder)
        # TODO: put the correct amount (not in the API yet)
        builder.price_unit = 10

        if values.get('carrier_id'):
            carrier = self.session.browse('delivery.carrier',
                                          values['carrier_id'])
            builder.carrier = carrier

        line = (0, 0, builder.get_line())
        values['order_line'].append(line)
        return values

    def finalize(self, map_record, values):
        sess = self.session
        values.setdefault('order_line', [])
        values = self._add_shipping_line(map_record, values)
        values['qoqa_order_line_ids'] = self.lines(map_record)
        onchange = self.get_connector_unit_for_model(SaleOrderOnChange)

        # TODO: create a gift card line when a payment has a method_id
        # which is a gift_card method
        # TODO: create voucher / promo
        return onchange.play(values, values['qoqa_order_line_ids'])

    def lines(self, map_record):
        """ Lines are composed of 2 list of dicts

        1 list is 'order_items', the other is 'items'.
        We keep the id of the 'item' and discard the one of the
        'order_items'.

        """
        lines = []
        for item in map_record.source['items']:
            nitem = item.copy()
            item_id = nitem['id']
            for order_item in map_record.source['order_items']:
                if order_item['item_id'] != item_id:
                    continue
                nitem.update(order_item)
            nitem.pop('id')  # remove id just to avoid confusion
            lines.append(nitem)

        map_child = self.get_connector_unit_for_model(
            self._map_child_class, 'qoqa.sale.order.line')
        items = map_child.get_items(lines, map_record, 'qoqa_order_line_ids',
                                    options=self.options)
        return items


@qoqa
class QoQaSaleOrderOnChange(SaleOrderOnChange):
    _model_name = 'qoqa.sale.order'


@qoqa
class SaleImportRule(ConnectorUnit):
    _model_name = ['qoqa.sale.order']

    def _check_max_days(self, record):
        """ Cancel the import of waiting for a payment for too long. """
        max_days = DAYS_BEFORE_CANCEL
        if max_days:
            order_id = record['id']
            order_date = iso8601_to_utc_datetime(record['created_at'])
            if order_date + timedelta(days=max_days) < datetime.now():
                raise NothingToDoJob('Import of the order %s canceled '
                                     'because it has not been paid since %d '
                                     'days' % (order_id, max_days))

    def check(self, record):
        """ Check whether the current sale order should be imported
        or not.

        States or QoQa are:

        * requested: an order has been created
        * paid: authorized on datatrans, not captured
        * confirmed: payment has been confirmed / captured by datatrans
        * processed: final state, when is order is delivered
        * cancelled: final state for cancellations

        How we will handle them:

        requested and paid
            We do not import them but delay the import for later until
            they are confirmed.

        confirmed
            They will be confirmed as soon as they are imported.

        processed
            We will short-circuit the workflow and set them directly to
            'done'. They are imported for the history.

        cancelled
            They are imported but directly cancelled, for the history.

        The automatic workflows do need to have the 'Confirm Sales Orders'
        field deactivated. The confirmation of sales orders is handled
        by the importer. This allows to keep the "paid" sales orders in draft
        while the importer confirms the "confirmed" ones.

        When an order has a status requested, we delay the import
        to later.

        This method only checks if we the sales orders should be imported
        and eventually raise a :py:class:`NothingToDoJob` or
        :py:class:`OrderImportRuleRetry`.

        It does not cancels sales orders or create payments, theses actions
        are done in the :py:meth:`SaleOrderImport._after_import` method.
        """
        import_states = (QOQA_STATUS_CONFIRMED, QOQA_STATUS_PROCESSED,
                         QOQA_STATUS_CANCELLED)
        if record['status_id'] in import_states:
            return
        self._check_max_days(record)

        states = (QOQA_STATUS_REQUESTED, QOQA_STATUS_PAID)
        if record['status_id'] in states:
            raise OrderImportRuleRetry('The payment of the order has not '
                                       'been confirmed.\nThe import will be '
                                       'retried later.')


@qoqa
class QoQaShippingLineBuilder(ShippingLineBuilder):
    _model_name = 'qoqa.sale.order'

    def __init__(self, environment):
        super(QoQaShippingLineBuilder, self).__init__(environment)
        self.carrier = None

    def get_line(self):
        line = super(QoQaShippingLineBuilder, self).get_line()
        if self.carrier:
            line['product_id'] = self.carrier.product_id.id
            line['name'] = self.carrier.name
        return line
