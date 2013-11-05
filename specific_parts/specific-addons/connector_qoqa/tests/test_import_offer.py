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

from .common import mock_api_responses, QoQaTransactionCase
from .data_offer import qoqa_offer
from .data_metadata import qoqa_shops
from ..unit.import_synchronizer import import_record


class test_import_offer(QoQaTransactionCase):
    """ Test the import of offers from QoQa """
    def setUp(self):
        super(test_import_offer, self).setUp()
        cr, uid = self.cr, self.uid
        self.Offer = self.registry('qoqa.offer')
        company_obj = self.registry('res.company')
        # create a new company so we'll check if it shop is linked
        # with the correct one when it is not the default one
        vals = {'name': 'Qtest', 'qoqa_id': 42}
        self.company_id = company_obj.create(cr, uid, vals)

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
        self.assertEquals(offer.pricelist_id.id, self.ref('product.list0'))
        self.assertEquals(offer.name, 'title')
        self.assertEquals(offer.description, '<p>content</p>')
        self.assertEquals(offer.note, '<p>Sav Schumf -Astavel</p>')
        self.assertEquals(offer.date_begin, '2013-10-14')
        self.assertEquals(offer.time_begin, 12)
        self.assertEquals(offer.date_end, '2013-10-16')
        self.assertEquals(offer.time_end, 12)
