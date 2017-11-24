# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json

from datetime import date, timedelta

from openerp import fields

from .common import recorder, QoQaTransactionCase


class TestCancelOrder(QoQaTransactionCase):

    def setUp(self):
        super(TestCancelOrder, self).setUp()
        self._create_order()

    def _create_order(self):
        method = self.env.ref('account.account_payment_method_manual_in')
        self.payment_mode = self.env['account.payment.mode'].create({
            'name': 'Paypal',
            'payment_method_id': method.id,
            'company_id': self.env.ref('base.main_company').id,
            'bank_account_link': 'variable',
            'qoqa_id': '1',
        })

        self.order_binding = self.env['qoqa.sale.order'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '6',
            'partner_id': self.env['res.partner'].create({'name': 'test'}).id,
            'payment_mode_id': self.payment_mode.id,
            'qoqa_payment_date': fields.Date.today(),
        })
        self.order = self.order_binding.openerp_id

    def test_cancel_order_direct(self):
        """ Canceled order directly canceled on QoQa """
        self.payment_mode.payment_cancellable_on_qoqa = True
        # if date_order is today and payment_cancellable_on_qoqa is True,
        # we want the order to be canceled as fast as possible so it
        # is not done with a job but directly
        with recorder.use_cassette('test_cancel_order_direct') as cassette:
            self.order.action_cancel()
            response_body = cassette.responses[0]['body']['string']
            self.assertEqual(json.loads(response_body), {'cancelled': True})

        self.assertEqual(self.order.state, 'cancel')

    def test_cancel_order_not_cancellable(self):
        """ Order delayed not cancellable delay cancellation on QoQa """
        self.payment_mode.payment_cancellable_on_qoqa = False
        # if payment_cancellable_on_qoqa is False we can delay the
        # cancellation

        with recorder.use_cassette('test_cancel_order_direct') as cassette:
            self.order.action_cancel()
            response_body = cassette.responses[0]['body']['string']
            self.assertEqual(json.loads(response_body), {'cancelled': True})

        self.assertEqual(self.order.state, 'cancel')

    def test_cancel_order_not_today(self):
        """ Order not delayed anymore if not from today"""
        self.payment_mode.payment_cancellable_on_qoqa = True
        # if date_order is before today, we still whant to cancell it on Qoqa
        self.order_binding.qoqa_payment_date = fields.Date.to_string(
            date.today() - timedelta(days=1)
        )

        with recorder.use_cassette('test_cancel_order_direct') as cassette:
            self.order.action_cancel()
            response_body = cassette.responses[0]['body']['string']
            self.assertEqual(json.loads(response_body), {'cancelled': True})

        self.assertEqual(self.order.state, 'cancel')
