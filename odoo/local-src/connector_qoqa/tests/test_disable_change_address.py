# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import mock
from .common import QoQaTransactionCase
from openerp import fields

MODULE_PATH = "openerp.addons.connector_qoqa.sale.exporter"
LABEL_MODULE_PATH = "openerp.addons.delivery_carrier_label_swiss_pp"
LABEL_WIZARD = ".models.stock"


class TestChangeShippingAddress(QoQaTransactionCase):
    def setUp(self):
        super(TestChangeShippingAddress, self).setUp()
        self._create_partner()

    def _create_partner(self):
        self.test_partner = self.env['res.partner'].create({'name': 'test'})
        self.env['qoqa.res.partner'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '1000003',
            'openerp_id': self.test_partner.id,
        })

    def _create_batch_picking(self):
        batch = self.env['stock.batch.picking'].create({
            'name': 'test batch',
        })
        return batch

    def _create_order(self, qoqa_id):
        method = self.env.ref('account.account_payment_method_manual_in')
        payment_mode = self.env['account.payment.mode'].create({
            'name': 'Paypal',
            'payment_method_id': method.id,
            'company_id': self.env.ref('base.main_company').id,
            'bank_account_link': 'variable',
            'qoqa_id': '1',
        })

        order_binding = self.env['qoqa.sale.order'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': str(qoqa_id),
            'partner_id': self.test_partner.id,
            'payment_mode_id': payment_mode.id,
            'qoqa_payment_date': fields.Date.today(),
        })
        order = order_binding.openerp_id
        order.order_line = [(0, 0, {
            'product_id': self.env['product.product'].search(
                [('type', '=', 'product')],
                limit=1,
            )
        })]
        order.ignore_exception = True
        return order

    @mock.patch(MODULE_PATH + '.disable_shipping_address_modification.delay')
    def test_job_on_batch(self, mocked_job):
        mocked_job.return_value = None
        order1 = self._create_order(6)
        order2 = self._create_order(7)
        batch = self._create_batch_picking()
        order1.action_confirm()
        order2.action_confirm()
        batch.picking_ids = [
            (4, order1.picking_ids[0].id, 0),
            (4, order2.picking_ids[0].id, 0),
        ]
        self.assertEquals(mocked_job.call_count, 1)

    @mock.patch(MODULE_PATH + '.disable_shipping_address_modification.delay')
    def test_batch_wizard_job_creation(self, mocked_job):
        mocked_job.return_value = None
        wizard = self.env['stock.batch.picking.creator'].create({
            'name': 'Unittest wizard',
        })
        order1 = self._create_order(6)
        order2 = self._create_order(7)
        order1.action_confirm()
        order2.action_confirm()
        picking_ids = order1.picking_ids.ids + order2.picking_ids.ids
        wizard.with_context(active_ids=picking_ids).action_create_batch()
        self.assertEquals(mocked_job.call_count, 1)

    @mock.patch(LABEL_MODULE_PATH + LABEL_WIZARD +
                '.DeliveryCarrierLabelGenerate._get_packs')
    @mock.patch(MODULE_PATH + '.disable_shipping_address_modification.delay')
    def test_label_wizard_job_creation(self, mocked_job, mocked_func):
        mocked_job.return_value = None
        mocked_func.return_value = []
        order1 = self._create_order(6)
        order2 = self._create_order(7)
        batch = self._create_batch_picking()
        order1.action_confirm()
        order2.action_confirm()
        batch.picking_ids = [
            (4, order1.picking_ids[0].id, 0),
            (4, order2.picking_ids[0].id, 0),
        ]
        wizard = self.DeliveryCarrierLabelGenerate = self.env[
            'delivery.carrier.label.generate'
        ].with_context(
            active_ids=batch.ids, active_model='stock.batch.picking'
        ).create({})
        wizard.action_generate_labels()
        self.assertNotEquals(mocked_job.call_count, 2)
