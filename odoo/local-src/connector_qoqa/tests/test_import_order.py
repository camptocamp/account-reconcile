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
    'product_id name price_unit product_uom_qty is_voucher'
)
ExpectedOrderLine.__new__.__defaults__ = (
    (False,) * len(ExpectedOrderLine._fields)
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
        self.payment_method = method
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
        self.fee_binding = self.env['qoqa.shipping.fee'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '1000001',
            'name': 'Drone delivery',
            'product_id': self.drone_product.id,
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
                      self.backend_record.id, 100000001)
        domain = [('qoqa_id', '=', '100000001')]
        order = self.env['qoqa.sale.order'].search(domain)
        order.ensure_one()

        # addresses or orders are imported as inactive
        address_model = self.env['qoqa.address'].with_context(
            active_test=False,
        )
        # expected relations
        domain = [('qoqa_id', '=', '1000001')]
        partner = self.env['qoqa.res.partner'].search(domain)
        partner.ensure_one()
        domain = [('qoqa_id', '=', '100000001')]
        shipping_address = address_model.search(domain)
        shipping_address.ensure_one()
        domain = [('qoqa_id', '=', '100000001')]
        invoice_address = address_model.search(domain)
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
                name='100000001',
                partner_id=partner.openerp_id,
                partner_shipping_id=shipping_address.openerp_id,
                partner_invoice_id=invoice_address.openerp_id,
                invoice_ref='ABCD1',
                client_order_ref='150414-UGLBGN',
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
                name='[product_9] Product 9',
                price_unit=6900,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=self.product_11_binding.openerp_id,
                name='[product_11] Product 11',
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
                name='[product_1] Product 1',
                price_unit=333,
                product_uom_qty=2,
            ),
            ExpectedOrderLine(
                product_id=self.product_2_binding.openerp_id,
                name='[product_2] Product 2',
                price_unit=333,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=self.drone_product,
                name='Drone delivery',
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
                name='[product_1] Product 1',
                price_unit=333,
                product_uom_qty=2,
            ),
            ExpectedOrderLine(
                product_id=self.drone_product,
                name='Drone delivery',
                price_unit=9,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=promo.product_id,
                name='Bon marketing (10000011)',
                price_unit=-9,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=promo.product_id,
                name='Bon marketing (10000011)',
                price_unit=-499,
                product_uom_qty=1,
            ),
        ]
        self.assert_records(expected, order.order_line)

    def _setup_voucher(self):
        voucher_product = self.env['product.product'].create({
            'name': 'Bon Cadeau',
            'default_code': 'BC',
        })
        self.backend_record.voucher_product_id = voucher_product
        self.env['account.payment.mode'].create({
            'name': 'Bon Cadeau',
            'payment_method_id': self.payment_method.id,
            'company_id': self.env.ref('base.main_company').id,
            'bank_account_link': 'variable',
            'qoqa_id': '9',
            'gift_card': True,
        })
        return voucher_product

    @freeze_time('2016-04-28 00:00:00')
    @recorder.use_cassette()
    def test_import_sale_order_with_voucher(self):
        voucher_product = self._setup_voucher()
        import_record(self.session, 'qoqa.sale.order',
                      self.backend_record.id, 4260998)
        domain = [('qoqa_id', '=', '4260998')]
        order = self.env['qoqa.sale.order'].search(domain)
        order.ensure_one()
        expected = [
            ExpectedOrderLine(
                product_id=self.product_1_binding.openerp_id,
                name='[product_1] Product 1',
                price_unit=79.,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=self.drone_product,
                name='Drone delivery',
                price_unit=9,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=voucher_product,
                name='Bon Cadeau (562614)',
                price_unit=-50.,
                product_uom_qty=1.,
                is_voucher=True,
            ),
        ]
        self.assert_records(expected, order.order_line)

    @freeze_time('2016-04-28 00:00:00')
    @recorder.use_cassette()
    def test_import_sale_order_with_voucher_partial(self):
        """ When a voucher/gift card is partially used """
        voucher_product = self._setup_voucher()
        import_record(self.session, 'qoqa.sale.order',
                      self.backend_record.id, 4260998)
        domain = [('qoqa_id', '=', '4260998')]
        order = self.env['qoqa.sale.order'].search(domain)
        order.ensure_one()
        expected = [
            ExpectedOrderLine(
                product_id=self.product_1_binding.openerp_id,
                name='[product_1] Product 1',
                price_unit=79.,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=self.drone_product,
                name='Drone delivery',
                price_unit=9,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=voucher_product,
                name='Bon Cadeau (562614)',
                price_unit=-33.,
                product_uom_qty=1.,
                is_voucher=True,
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
