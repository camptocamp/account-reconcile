# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import json

from .common import recorder, QoQaTransactionCase


class TestExportRefund(QoQaTransactionCase):

    def setUp(self):
        super(TestExportRefund, self).setUp()

        self.env['sale.exception'].search([]).write({'active': False})

        self.customer_partner = self.env['res.partner'].create({
            'name': 'Unittest customer partner',
        })

        self.product_1 = self.env['product.product'].create({
            'name': 'Unittest P1'
        })
        self.create_binding_no_export(
            'qoqa.product.product', self.product_1.id, '11'
        )

        self.sale = self.env['sale.order'].create({
            'partner_id': self.customer_partner.id,
            'partner_invoice_id': self.customer_partner.id,
            'partner_shipping_id': self.customer_partner.id,
            'order_line': [(0, 0, {
                'name': self.product_1.name,
                'product_id': self.product_1.id,
                'product_uom_qty': 5.0,
                'product_uom': self.product_1.uom_id.id,
                'price_unit': 1,
                'tax_id': [],

            })],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        self.create_binding_no_export(
            'qoqa.sale.order', self.sale.id, '1',
            qoqa_payment_id='1'
        )
        self.sale.action_confirm()
        self.sale.action_invoice_create()

    def test_export_refund(self):
        invoice = self.sale.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.sale_order_ids, self.sale)
        refund = invoice.refund()
        self.assertEqual(refund.refund_from_invoice_id, invoice)
        with recorder.use_cassette('test_export_refund') as cassette:
            refund.signal_workflow('invoice_open')
            request = cassette.requests[0]
            self.assertEqual(json.loads(request.body), {'amount': 5.0})
            self.assertEqual(refund.transaction_id, '7')
            move_lines = self.env['account.move.line'].search(
                [('move_id', '=', refund.move_id.id),
                 ('account_id', '=', refund.account_id.id)]
            )
            for line in move_lines:
                self.assertEqual(line.transaction_ref, '7')

    def test_cancel_refund(self):
        invoice = self.sale.invoice_ids
        self.assertEqual(len(invoice), 1)
        self.assertEqual(invoice.sale_order_ids, self.sale)
        refund = invoice.refund()
        # allow to cancel entries
        refund.journal_id.update_posted = True
        self.assertEqual(refund.refund_from_invoice_id, invoice)
        with recorder.use_cassette('test_export_refund'):
            refund.signal_workflow('invoice_open')

        with recorder.use_cassette('test_cancel_refund') as cassette:
            refund.signal_workflow('invoice_cancel')
            body = cassette.responses[0]['body']['string']
            self.assertEqual(json.loads(body), {'cancelled': True})
