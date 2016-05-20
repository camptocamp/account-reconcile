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
from .data_offer import qoqa_offer
from .data_metadata import qoqa_shops
from .data_product import qoqa_product
from ..unit.import_synchronizer import import_record


@mock.patch('urllib2.urlopen', mock.Mock(return_value=MockResponseImage('')))
class test_import_offer(QoQaTransactionCase):
    """ Test the import of offers from QoQa """
    def setUp(self):
        super(test_import_offer, self).setUp()
        self.Offer = self.registry('qoqa.offer')
        self.OfferPos = self.registry('qoqa.offer.position')
        self.setUpCompany()

    def test_import_offer(self):
        """ Import an Offer """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_offer, qoqa_shops):
            import_record(self.session, 'qoqa.offer',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        offer_ids = self.Offer.search(cr, uid, domain)
        self.assertEquals(len(offer_ids), 1)
        offer = self.Offer.browse(cr, uid, offer_ids[0])
        self.assertEquals(offer.qoqa_shop_id.qoqa_id, '100')
        self.assertEquals(offer.pricelist_id.id, self.pricelist_id)
        self.assertEquals(offer.title, 'title')
        self.assertEquals(offer.description, '<p>content</p>')
        self.assertEquals(offer.note, '<p>Sav Schumf -Astavel</p>')
        self.assertEquals(offer.date_begin, '2013-10-14')
        self.assertEquals(offer.time_begin, 12)
        self.assertEquals(offer.date_end, '2013-10-16')
        self.assertEquals(offer.time_end, 12)

    def test_import_offer_position(self):
        """ Import an offer position """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_offer, qoqa_shops, qoqa_product):
            import_record(self.session, 'qoqa.offer.position',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        pos_ids = self.OfferPos.search(cr, uid, domain)
        self.assertEquals(len(pos_ids), 1)
        pos = self.OfferPos.browse(cr, uid, pos_ids[0])
        self.assertEquals(pos.offer_id.qoqa_id, '99999999')
        self.assertEquals(pos.regular_price_type, 'normal')
        self.assertEquals(pos.product_tmpl_id.qoqa_bind_ids[0].qoqa_id,
                          '99999999')

        self.assertEquals(len(pos.variant_ids), 1)
        pos_var = pos.variant_ids[0]
        self.assertEquals(pos_var.product_id.qoqa_bind_ids[0].qoqa_id,
                          '99999999')
        self.assertEquals(pos_var.quantity, 100)
