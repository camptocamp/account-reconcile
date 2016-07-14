# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import namedtuple

import mock

from freezegun import freeze_time

from openerp.addons.connector.tests.common import mock_job_delay_to_direct

from openerp.addons.connector_qoqa.unit.importer import import_record

from .common import recorder, QoQaTransactionCase

ExpectedOrder = namedtuple(
    'ExpectedOrder',
    'name partner_id partner_invoice_id partner_shipping_id invoice_ref '
    'client_order_ref qoqa_amount_total qoqa_shop_id offer_id '
    'qoqa_payment_amount'
)
ExpectedOrderLine = namedtuple(
    'ExpectedOrderLine',
    'product_id price_unit product_uom_qty'
)


class TestImportOrder(QoQaTransactionCase):
    """ Test the import of orders from QoQa """

    def setUp(self):
        super(TestImportOrder, self).setUp()
        self.Order = self.env['sale.order']
        self.setup_company()
        self.sync_metadata()
        self.setup_order_dependencies()

    def setup_order_dependencies(self):
        method = self.env.ref('account.account_payment_method_manual_in')
        self.payment_mode = self.env['account.payment.mode'].create({
            'name': 'Paypal',
            'payment_method_id': method.id,
            'company_id': self.env.ref('base.main_company').id,
            'bank_account_link': 'variable',
            'qoqa_id': '1',
        })

        # delivery by drone
        self.drone_product = self.env['product.product'].create({
            'name': 'Drone',
            'default_code': 'drone',
        })
        self.fee_binding = self.env['qoqa.shipper.fee'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '1000001',
            'delivery_type': 'fixed',
            'name': 'Drone delivery',
            'product_id': self.drone_product.id,
            'partner_id': self.env.ref('base.main_company').partner_id.id,
        })
        self.product_1_binding = self.env['qoqa.product.product'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '100001',
            'name': 'Product 1',
            'default_code': 'product_1',
        })
        self.product_2_binding = self.env['qoqa.product.product'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '100002',
            'name': 'Product 2',
            'default_code': 'product_2',
        })
        self.product_9_binding = self.env['qoqa.product.product'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '100009',
            'name': 'Product 9',
            'default_code': 'product_9',
        })
        self.product_11_binding = self.env['qoqa.product.product'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '100011',
            'name': 'Product 11',
            'default_code': 'product_11',
        })

    @freeze_time('2016-04-28 00:00:00')
    def test_import_sale_order_batch(self):
        from_date = '2016-04-10 00:00:00'
        self.backend_record.import_sale_order_from_date = from_date
        batch_job_path = ('openerp.addons.connector_qoqa.unit'
                          '.importer.import_batch')
        record_job_path = ('openerp.addons.connector_qoqa.unit'
                           '.importer.import_record')
        # execute the batch job directly and replace the record import
        # by a mock (individual import is tested elsewhere)
        with recorder.use_cassette('test_import_order_batch') as cassette, \
                mock_job_delay_to_direct(batch_job_path), \
                mock.patch(record_job_path) as import_record_mock:
            self.backend_record.import_sale_order()

            # 3 batch requests to do (1 per week)
            self.assertEqual(len(cassette.requests), 3)
            # the batch jobs return 3 records
            self.assertEqual(import_record_mock.delay.call_count, 3)

    @freeze_time('2016-04-28 00:00:00')
    @recorder.use_cassette()
    def test_import_sale_order(self):
        """ Import a sale order """
        # prepare dependencies

        # import
        import_record(self.session, 'qoqa.sale.order',
                      self.backend_record.id, 1)
        domain = [('qoqa_id', '=', '1')]
        order = self.env['qoqa.sale.order'].search(domain)
        order.ensure_one()

        # expected relations
        domain = [('qoqa_id', '=', '1000001')]
        partner = self.env['qoqa.res.partner'].search(domain)
        partner.ensure_one()
        domain = [('qoqa_id', '=', '100000001')]
        shipping_address = self.env['qoqa.address'].search(domain)
        shipping_address.ensure_one()
        domain = [('qoqa_id', '=', '100000001')]
        invoice_address = self.env['qoqa.address'].search(domain)
        invoice_address.ensure_one()
        domain = [('qoqa_id', '=', '3')]
        shop = self.env['qoqa.shop'].search(domain)
        shop.ensure_one()
        domain = [('qoqa_id', '=', '1000005')]
        offer = self.env['qoqa.offer'].search(domain)
        offer.ensure_one()

        # check order
        expected = [
            ExpectedOrder(
                name='00000001',
                partner_id=partner.openerp_id,
                partner_shipping_id=shipping_address.openerp_id,
                partner_invoice_id=invoice_address.openerp_id,
                invoice_ref='ABCD1',
                client_order_ref='ABCD1',
                qoqa_amount_total=20700.0,
                qoqa_shop_id=shop,
                offer_id=offer,
                qoqa_payment_amount=6900,
            ),
        ]
        self.assert_records(expected, order)

        # check lines
        expected = [
            ExpectedOrderLine(
                product_id=self.product_9_binding.openerp_id,
                price_unit=6900,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=self.product_11_binding.openerp_id,
                price_unit=6900,
                product_uom_qty=2,
            ),
        ]
        self.assert_records(expected, order.order_line)

    @freeze_time('2016-04-28 00:00:00')
    @recorder.use_cassette()
    def test_import_sale_order_with_shipping(self):
        import_record(self.session, 'qoqa.sale.order',
                      self.backend_record.id, 2)
        domain = [('qoqa_id', '=', '2')]
        order = self.env['qoqa.sale.order'].search(domain)
        order.ensure_one()
        # check lines
        expected = [
            ExpectedOrderLine(
                product_id=self.product_1_binding.openerp_id,
                price_unit=333,
                product_uom_qty=2,
            ),
            ExpectedOrderLine(
                product_id=self.product_2_binding.openerp_id,
                price_unit=333,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=self.drone_product,
                price_unit=12,
                product_uom_qty=1,
            ),
        ]
        self.assert_records(expected, order.order_line)

    @freeze_time('2016-04-28 00:00:00')
    @recorder.use_cassette()
    def test_import_sale_order_with_discount(self):
        promo = self.env.ref('connector_qoqa.promo_type_marketing')
        import_record(self.session, 'qoqa.sale.order',
                      self.backend_record.id, 16)
        domain = [('qoqa_id', '=', '16')]
        order = self.env['qoqa.sale.order'].search(domain)
        order.ensure_one()
        # check lines
        expected = [
            ExpectedOrderLine(
                product_id=self.product_1_binding.openerp_id,
                price_unit=333,
                product_uom_qty=2,
            ),
            ExpectedOrderLine(
                product_id=self.drone_product,
                price_unit=9,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=promo.product_id,
                price_unit=-9,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=promo.product_id,
                price_unit=-499,
                product_uom_qty=1,
            ),
        ]
        self.assert_records(expected, order.order_line)

    def test_sale_order_invoice_transaction_id(self):
        partner = self.env['res.partner'].create({'name': 'Test'})
        product = self.product_1_binding.openerp_id
        sale = self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 5.0,
                'product_uom': product.uom_id.id,
            })],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        self.create_binding_no_export(
            'qoqa.sale.order', sale.id,
            qoqa_id='99',
            qoqa_payment_id='123456789',
        )
        self.env['sale.exception'].search([]).write({'active': False})
        sale.action_confirm()
        sale.action_invoice_create()
        invoice = sale.invoice_ids
        self.assertEquals(invoice.transaction_id, '123456789')
        invoice.signal_workflow('invoice_open')
        for move_line in invoice.move_id.line_ids:
            # we need the transaction_id only on those lines:
            if move_line.account_id == invoice.account_id:
                self.assertEquals(move_line.transaction_ref, '123456789')
