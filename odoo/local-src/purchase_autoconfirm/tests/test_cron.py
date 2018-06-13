# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from openerp.tests import SavepointCase
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class TestCron(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCron, cls).setUpClass()
        cls.purchase_obj = cls.env["purchase.order"]
        cls.invoice_obj = cls.env["account.invoice"]
        cls.partner_id = cls.env.ref('base.res_partner_1')
        cls.product_id_1 = cls.env.ref('product.product_product_8')
        cls.product_id_1.purchase_method = 'purchase'
        cls.product_id_2 = cls.env.ref('product.product_product_11')
        cls.product_id_2.purchase_method = 'purchase'
        cls.payment_mode_id = cls.env.ref(
            'account_payment_mode.payment_mode_outbound_ct1'
        )

    def create_PO(self):
        po_vals = {
            'partner_id': self.partner_id.id,
            'payment_mode_id': self.payment_mode_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_id_1.name,
                    'product_id': self.product_id_1.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_1.uom_po_id.id,
                    'price_unit': 500.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                }),
                (0, 0, {
                    'name': self.product_id_2.name,
                    'product_id': self.product_id_2.id,
                    'product_qty': 5.0,
                    'product_uom': self.product_id_2.uom_po_id.id,
                    'price_unit': 250.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                })],
        }
        return self.purchase_obj.create(po_vals)

    def create_invoice(self, purchase):
        invoice_account = self.env['account.account'].search([
            ('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)
        ], limit=1).id
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_id.id,
            'account_id': invoice_account,
            'type': 'in_invoice',
            'purchase_id': purchase.id,
        })
        invoice.purchase_order_change()
        return invoice

    def test__check_status_pickings(self):
        purchase = self.create_PO()
        purchase.button_confirm()
        self.assertTrue(purchase.picking_ids)
        self.assertFalse(purchase._check_status_pickings())
        purchase.picking_ids.do_transfer()
        self.assertTrue(purchase._check_status_pickings())

    def test__check_status_invoices(self):
        purchase = self.create_PO()
        purchase.button_confirm()
        invoice = self.create_invoice(purchase)
        self.assertTrue(purchase.invoice_ids)
        self.assertFalse(purchase._check_status_invoices())
        invoice.state = 'paid'
        self.assertTrue(purchase._check_status_invoices())

    def test__check_statuses(self):
        purchase = self.create_PO()
        purchase.button_confirm()
        purchase.picking_ids.do_transfer()
        invoice = self.create_invoice(purchase)
        invoice.state = 'paid'
        self.assertTrue(purchase._check_statuses())
