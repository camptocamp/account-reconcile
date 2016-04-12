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
    'client_order_ref qoqa_amount_total qoqa_shop_id offer_id carrier_id'
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

        # ship_ref = 'connector_ecommerce.product_product_shipping'
        # self.ship_product = self.env.ref(ship_ref)
        # marketing_ref = 'qoqa_base_data.product_product_marketing_coupon'
        # self.marketing_product = self.env.ref(marketing_ref)

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
        drone_product = self.env['product.product'].create({
            'name': 'Drone',
            'default_code': 'drone',
        })
        carrier_binding = self.env['qoqa.shipper.service'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '1',
            'delivery_type': 'fixed',
            'name': 'Drone delivery',
            'product_id': drone_product.id,
            'partner_id': self.env.ref('base.main_company').partner_id.id,
        })
        product_1_binding = self.env['qoqa.product.product'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '9',
            'name': 'Product 1',
            'default_code': 'product_1',
        })
        product_2_binding = self.env['qoqa.product.product'].create({
            'backend_id': self.backend_record.id,
            'qoqa_id': '11',
            'name': 'Product 2',
            'default_code': 'product_2',
        })

        # import
        import_record(self.session, 'qoqa.sale.order',
                      self.backend_record.id, 1)
        domain = [('qoqa_id', '=', '1')]
        order = self.env['qoqa.sale.order'].search(domain)
        order.ensure_one()

        # expected relations
        domain = [('qoqa_id', '=', '1000001')]
        partner = self.env['qoqa.res.partner'].search(domain)
        domain = [('qoqa_id', '=', '100000001')]
        shipping_address = self.env['qoqa.address'].search(domain)
        domain = [('qoqa_id', '=', '100000001')]
        invoice_address = self.env['qoqa.address'].search(domain)
        domain = [('qoqa_id', '=', '3')]
        shop = self.env['qoqa.shop'].search(domain)
        domain = [('qoqa_id', '=', '5')]
        offer = self.env['qoqa.offer'].search(domain)

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
                carrier_id=carrier_binding.openerp_id,
            ),
        ]
        self.assert_records(expected, order)

        # check lines
        expected = [
            ExpectedOrderLine(
                product_id=product_1_binding.openerp_id,
                price_unit=6900,
                product_uom_qty=1,
            ),
            ExpectedOrderLine(
                product_id=product_2_binding.openerp_id,
                price_unit=6900,
                product_uom_qty=2,
            ),
        ]
        self.assert_records(expected, order.order_line)


    # def test_import_order(self):
    #     """ Import a sales order """
    #     cr, uid = self.cr, self.uid
    #     data = (qoqa_order, qoqa_product, qoqa_offer,
    #             qoqa_address, qoqa_shops, qoqa_promo)
    #     with mock_api_responses(*data):
    #         import_record(self.session, 'qoqa.sale.order',
    #                       self.backend_id, 99999999)
    #     domain = [('qoqa_id', '=', '99999999')]
    #     # sales order
    #     qsale_ids = self.QSale.search(cr, uid, domain)
    #     self.assertEquals(len(qsale_ids), 1)
    #     qsale = self.QSale.browse(cr, uid, qsale_ids[0])
    #     self.assertEquals(qsale.invoice_ref, 'XRIHJQ')
    #     # lines
    #     lines = qsale.order_line
    #     self.assertEquals(len(lines), 3)
    #     ship_line = prod_line = promo_line = None
    #     for line in lines:
    #         if line.product_id.id == self.ship_product_id:
    #             ship_line = line
    #         elif line.product_id.id == self.marketing_product_id:
    #             promo_line = line
    #         else:
    #             prod_line = line
    #     self.assertTrue(ship_line and promo_line and prod_line)
    #     # product line
    #     position = prod_line.offer_position_id
    #     self.assertTrue(position)
    #     self.assertEquals(prod_line.price_unit, 17.5)  # 105 / 6 (lot)
    #     self.assertEquals(prod_line.product_uom_qty, 12)
    #     self.assertEquals(prod_line.custom_text, 'custom text')
    #     # shipping line
    #     self.assertEquals(ship_line.price_unit, 6)
    #     self.assertEquals(ship_line.product_uom_qty, 1)
    #     # promo line
    #     self.assertEquals(promo_line.price_unit, -9.5)
    #     self.assertEquals(promo_line.product_uom_qty, 1)
