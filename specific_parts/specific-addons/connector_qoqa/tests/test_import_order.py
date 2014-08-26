# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import mock
from .common import mock_api_responses, QoQaTransactionCase, MockResponseImage
from .data_metadata import qoqa_shops
from .data_order import qoqa_order
from .data_partner import qoqa_address
from .data_offer import qoqa_offer
from .data_product import qoqa_product
from .data_promo import qoqa_promo
from ..unit.import_synchronizer import import_record


@mock.patch('urllib2.urlopen', mock.Mock(return_value=MockResponseImage('')))
class test_import_order(QoQaTransactionCase):
    """ Test the import of order from QoQa  """

    def setUp(self):
        super(test_import_order, self).setUp()
        self.setUpCompany()
        self.QSale = self.registry('qoqa.sale.order')
        self.ship_product_id = self.ref('connector_ecommerce.product_product_shipping')
        self.marketing_product_id = self.ref('qoqa_base_data.product_product_marketing_coupon')

    def test_import_order(self):
        """ Import a sales order """
        cr, uid = self.cr, self.uid
        data = (qoqa_order, qoqa_product, qoqa_offer,
                qoqa_address, qoqa_shops, qoqa_promo)
        with mock_api_responses(*data):
            import_record(self.session, 'qoqa.sale.order',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        # sales order
        qsale_ids = self.QSale.search(cr, uid, domain)
        self.assertEquals(len(qsale_ids), 1)
        qsale = self.QSale.browse(cr, uid, qsale_ids[0])
        self.assertEquals(qsale.invoice_ref, 'XRIHJQ')
        # lines
        lines = qsale.order_line
        self.assertEquals(len(lines), 3)
        ship_line = prod_line = promo_line = None
        for line in lines:
            if line.product_id.id == self.ship_product_id:
                ship_line = line
            elif line.product_id.id == self.marketing_product_id:
                promo_line = line
            else:
                prod_line = line
        self.assertTrue(ship_line and promo_line and prod_line)
        # product line
        position = prod_line.offer_position_id
        self.assertTrue(position)
        self.assertEquals(prod_line.price_unit, 17.5)  # 105 / 6 (lot)
        self.assertEquals(prod_line.product_uom_qty, 12)
        self.assertEquals(prod_line.custom_text, 'custom text')
        # shipping line
        self.assertEquals(ship_line.price_unit, 6)
        self.assertEquals(ship_line.product_uom_qty, 1)
        # promo line
        self.assertEquals(promo_line.price_unit, -9.5)
        self.assertEquals(promo_line.product_uom_qty, 1)
