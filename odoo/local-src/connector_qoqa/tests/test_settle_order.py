# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import mock

from openerp import fields

from openerp.addons.connector_qoqa.sale.common import settle_sales_order
from .common import recorder, QoQaTransactionCase


class TestSettleOrder(QoQaTransactionCase):

    def setUp(self):
        super(TestSettleOrder, self).setUp()
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
        self.order.action_confirm()

    def test_settle_order(self):
        """ Settle order """
        self.payment_mode.payment_settlable_on_qoqa = True
        settle_job_path = ('openerp.addons.connector_qoqa.sale'
                           '.common.settle_sales_order')
        with mock.patch(settle_job_path) as settle_order_mock:
            self.order.action_done()
            settle_order_mock.delay.assert_called_with(
                mock.ANY, 'qoqa.sale.order', self.order_binding.id,
                priority=1
            )

        with recorder.use_cassette('test_settle_order'):
            settle_sales_order(self.session, 'qoqa.sale.order',
                               self.order_binding.id)
