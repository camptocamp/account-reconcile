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
from .data_partner import qoqa_user, qoqa_address
from ..unit.import_synchronizer import import_record


@mock.patch('urllib2.urlopen', mock.Mock(return_value=MockResponseImage('')))
class test_import_partner(QoQaTransactionCase):
    """ Test the import of partner from QoQa.  """
    def setUp(self):
        super(test_import_partner, self).setUp()
        self.QPartner = self.registry('qoqa.res.partner')
        self.Partner = self.registry('res.partner')
        self.QAddress = self.registry('qoqa.address')
        self.setUpCompany()

    def test_import_partner(self):
        """ Import a partner (QoQa user) """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_user, qoqa_shops):
            import_record(self.session, 'qoqa.res.partner',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        qpartner_ids = self.QPartner.search(cr, uid, domain)
        self.assertEquals(len(qpartner_ids), 1)
        qpartner = self.QPartner.browse(cr, uid, qpartner_ids[0])
        self.assertEquals(qpartner.name, 'Mykonos (christos.k@bluewin.ch-test)')
        self.assertEquals(qpartner.qoqa_name, 'Mykonos')
        self.assertEquals(qpartner.email, 'christos.k@bluewin.ch-test')
        self.assertTrue(qpartner.is_company)
        self.assertEquals(qpartner.created_at, '2008-06-02 15:40:17')
        self.assertEquals(qpartner.updated_at, '2013-11-19 09:39:52')
        self.assertEquals(qpartner.origin_shop_id.name, 'Qtest.ch')
        self.assertEquals(qpartner.lang, 'fr_FR')
        self.assertEquals(qpartner.qoqa_status, 'active')
        # addresses are imported at the same time for the first import
        # of the customer
        addresses = qpartner.child_ids
        # 4 addresses are active
        self.assertEquals(len(addresses), 4)

    def test_import_twice(self):
        """ Import a partner twice, the second import is skipped"""
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_user, qoqa_shops):
            import_record(self.session, 'qoqa.res.partner',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        qpartner_ids = self.QPartner.search(cr, uid, domain)
        self.assertEquals(len(qpartner_ids), 1)
        qpartner = self.QPartner.browse(cr, uid, qpartner_ids[0])
        with mock_api_responses(qoqa_user, qoqa_shops):
            import_record(self.session, 'qoqa.res.partner',
                          self.backend_id, 99999999)
        qpartner2_ids = self.QPartner.search(cr, uid, domain)
        qpartner2 = self.QPartner.browse(cr, uid, qpartner2_ids[0])
        self.assertEquals(qpartner_ids, qpartner2_ids)
        self.assertEquals(qpartner.sync_date, qpartner2.sync_date)

    def test_import_address(self):
        """ Import an address (with dependencies) """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_address, qoqa_shops):
            import_record(self.session, 'qoqa.address',
                          self.backend_id, 999999991)
        domain = [('qoqa_id', '=', '999999991')]
        qaddr_ids = self.QAddress.search(cr, uid, domain)
        self.assertEquals(len(qaddr_ids), 1)
        qaddr = self.QAddress.browse(cr, uid, qaddr_ids[0])
        self.assertEquals(qaddr.name, 'Guewen Baconnier')
        self.assertEquals(qaddr.street, 'Grand Rue 3')
        self.assertEquals(qaddr.street2, '--')
        self.assertEquals(qaddr.city, 'Orbe')
        self.assertEquals(qaddr.zip, '1350')
        self.assertEquals(qaddr.country_id.id, self.ref('base.ch'))
        self.assertEquals(qaddr.created_at, '2013-06-10 07:54:15')
        self.assertEquals(qaddr.updated_at, '2013-06-10 07:54:15')
        partner = qaddr.parent_id
        self.assertTrue(partner.is_company)

    def test_import_on_existing(self):
        """ Import a partner, should bind on an existing with same email """
        cr, uid = self.cr, self.uid
        p_id = self.Partner.create(cr, uid,
                                   {'name': 'Guewen',
                                    'email': 'guewen@gmail.com-test',
                                    'is_company': True})
        self.Partner.create(cr, uid,
                            {'name': 'Guewen address 1',
                             'parent_id': p_id})
        with mock_api_responses(qoqa_address, qoqa_shops):
            import_record(self.session, 'qoqa.address',
                          self.backend_id, 999999991)
        domain = [('qoqa_id', '=', '999999991')]
        qaddr_ids = self.QAddress.search(cr, uid, domain)
        self.assertEquals(len(qaddr_ids), 1)
        qaddr = self.QAddress.browse(cr, uid, qaddr_ids[0])
        partner = qaddr.parent_id
        self.assertEquals(partner.id, p_id)
        # filter on active addresses only
        self.assertEquals(len(partner.child_ids), 2)
