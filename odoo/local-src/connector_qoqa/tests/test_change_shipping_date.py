# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import fields
from openerp.exceptions import UserError, MissingError
from .common import QoQaTransactionCase
from openerp.addons.connector.session import ConnectorSession
from ..connector import get_environment
from ..sale.importer import QoQaSaleShippingDateChanger


class TestChangeShippingAddress(QoQaTransactionCase):
    def setUp(self):
        super(TestChangeShippingAddress, self).setUp()
        self._create_partner()
        self._create_order()
        self.new_date = "2018-09-09"

    def _create_partner(self):
        self.test_partner = self.env['res.partner'].create({
            'name': 'test'
        })
        self.env['qoqa.res.partner'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '1000003',
            'openerp_id': self.test_partner.id,
        })

    def _create_order(self):
        method = self.env.ref('account.account_payment_method_manual_in')
        self.payment_mode = self.env['account.payment.mode'].create(
            {
                'name': 'Paypal',
                'payment_method_id': method.id,
                'company_id': self.env.ref('base.main_company').id,
                'bank_account_link': 'variable',
                'qoqa_id': '1',
            }
        )

        self.order_binding = self.env['qoqa.sale.order'].create(
            {
                'backend_id': self.backend_record.id,
                'qoqa_id': '6',
                'partner_id': self.test_partner.id,
                'payment_mode_id': self.payment_mode.id,
                'qoqa_payment_date': fields.Date.today(),
            }
        )
        self.order = self.order_binding.openerp_id
        self.order.order_line = [(0, 0, {
            'product_id': self.env['product.product'].search(
                [('type', '=', 'product')],
                limit=1,
            )
        })]
        self.order.ignore_exception = True

    def _create_batch_picking(self):
        batch = self.env['stock.batch.picking'].create({
            'name': 'test batch',
        })
        return batch

    def _create_label(self, res_id):
        self.env['shipping.label'].create({
            'res_id': res_id,
            'res_model': 'stock.picking',
            'attachment_id': 1,
        })

    def _get_connector_unit(self):
        session = ConnectorSession.from_env(self.env)
        with get_environment(
            session,
            'qoqa.sale.order',
            self.backend_record.id
        ) as connector_env:
            connector_unit = connector_env.get_connector_unit(
                QoQaSaleShippingDateChanger,
            )
        return connector_unit

    def test_change_shipping_date(self):
        self.order.action_confirm()
        self.assertNotEqual(
            self.order.picking_ids.mapped("min_date"),
            ['2018-09-09 12:00:00'],
        )
        connector_unit = self._get_connector_unit()
        connector_unit.try_change(
            self.order_binding.qoqa_id,
            self.new_date
        )
        self.assertEqual(
            self.order.picking_ids.mapped("min_date"),
            ['2018-09-09 12:00:00'],
        )
        self.assertEqual(
            self.order.picking_ids.mapped("picking_type_id"),
            self.env.ref('qoqa_base_data.picking_type_postpone_delivery'),
        )

    def test_change_shipping_address_batch(self):
        self.order.action_confirm()
        self.assertNotEqual(
            self.order.picking_ids.mapped("min_date"),
            ['2018-09-09 12:00:00'],
        )
        batch = self._create_batch_picking()
        batch.picking_ids = [(4, self.order.picking_ids[0].id, 0)]
        connector_unit = self._get_connector_unit()
        with self.assertRaises(UserError) as error:
            connector_unit.try_change(
                self.order_binding.qoqa_id,
                self.new_date
            )
        self.assertEqual(
            error.exception.name,
            'Impossible to change shipping date'
        )

    def test_change_shipping_address_label(self):
        self.order.action_confirm()
        self.assertNotEqual(
            self.order.picking_ids.mapped("min_date"),
            ['2018-09-09 12:00:00'],
        )
        self._create_label(self.order.picking_ids[0].id)
        connector_unit = self._get_connector_unit()
        with self.assertRaises(UserError) as error:
            connector_unit.try_change(
                self.order_binding.qoqa_id,
                self.new_date
            )
        self.assertEqual(
            error.exception.name,
            'Impossible to change shipping date'
        )

    def test_change_shipping_address_pickings(self):
        self.assertFalse(self.order.picking_ids)
        connector_unit = self._get_connector_unit()
        with self.assertRaises(MissingError) as error:
            connector_unit.try_change(
                self.order_binding.qoqa_id,
                self.new_date
            )
        self.assertEqual(
            error.exception.name,
            'Sale order with id {} has no pickings'.format(
                self.order.qoqa_bind_ids.qoqa_id)
        )
