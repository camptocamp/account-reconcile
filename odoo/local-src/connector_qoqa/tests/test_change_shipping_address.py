# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import fields
from openerp.exceptions import UserError
from .common import QoQaTransactionCase
from openerp.addons.connector.session import ConnectorSession
from ..connector import get_environment
from ..sale.importer import QoQaSaleShippingAddressChanger


class TestChangeShippingAddress(QoQaTransactionCase):
    def setUp(self):
        super(TestChangeShippingAddress, self).setUp()
        self._create_partner()
        self._create_order()
        self.new_address = {
            "data": {
                "id": 2,
                "attributes": {
                    "service": "standard",
                    "city": "Hauterive",
                    "kind": "personal",
                    "order_user_id": 1000001,
                    "user_id": 1000003,
                    "zip": "2068",
                    "firstname": "John",
                    "alias": False,
                    "lastname": "Doe",
                    "street2": False,
                    "country_id": 1,
                    "service_client_number": False,
                    "updated_at": "2016-10-10T12:47:56.000+02:00",
                    "phone": "0781733455",
                    "street": "Chemin du bois 17",
                    "company_name": False,
                    "gender": 1,
                    "country": "Suisse",
                    "digicode": False,
                    "created_at": "2016-10-10T12:47:56.000+02:00",
                }
            }
        }

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
                QoQaSaleShippingAddressChanger,
            )
        return connector_unit

    def test_change_shipping_address(self):
        self.assertEqual(self.order.partner_shipping_id.name, 'test')
        connector_unit = self._get_connector_unit()
        connector_unit.try_change(
            self.order_binding.qoqa_id,
            self.new_address
        )
        self.assertEqual(self.order.partner_shipping_id.name, 'John Doe')

    def test_change_shipping_address_batch(self):
        self.assertEqual(self.order.partner_shipping_id.name, 'test')
        batch = self._create_batch_picking()
        self.order.action_confirm()
        batch.picking_ids = [(4, self.order.picking_ids[0].id, 0)]
        connector_unit = self._get_connector_unit()
        with self.assertRaises(UserError) as error:
            connector_unit.try_change(
                self.order_binding.qoqa_id,
                self.new_address
            )
        self.assertEqual(
            error.exception.name,
            'Impossible to change shipping address'
        )

    def test_change_shipping_address_label(self):
        self.assertEqual(self.order.partner_shipping_id.name, 'test')
        self.order.action_confirm()
        self._create_label(self.order.picking_ids[0].id)
        connector_unit = self._get_connector_unit()
        with self.assertRaises(UserError) as error:
            connector_unit.try_change(
                self.order_binding.qoqa_id,
                self.new_address
            )
        self.assertEqual(
            error.exception.name,
            'Impossible to change shipping address'
        )
