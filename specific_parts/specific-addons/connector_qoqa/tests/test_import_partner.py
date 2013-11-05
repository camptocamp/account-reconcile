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
from openerp.addons.connector.session import ConnectorSession
from .common import mock_api_responses, QoQaTransactionCase
from .data_partner import qoqa_user, qoqa_address
from ..unit.import_synchronizer import import_record


class test_import_partner(QoQaTransactionCase):
    """ Test the import of partner from QoQa (actually
    QoQa Shops).
    """
    def setUp(self):
        super(test_import_partner, self).setUp()
        self.QPartner = self.registry('qoqa.res.partner')
        self.Partner = self.registry('res.partner')
        self.QAddress = self.registry('qoqa.address')

    def test_import_partner(self):
        """ Import a partner (QoQa user) """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_user):
            import_record(self.session, 'qoqa.res.partner',
                          self.backend_id, 9999999)
        domain = [('qoqa_id', '=', '9999999')]
        qpartner_ids = self.QPartner.search(cr, uid, domain)
        self.assertEquals(len(qpartner_ids), 1)
        qpartner = self.QPartner.browse(cr, uid, qpartner_ids[0])
        self.assertEquals(qpartner.name, 'Christos Kornaros')
        self.assertEquals(qpartner.qoqa_name, 'Mykonos')
        self.assertEquals(qpartner.email, 'christos.k@bluewin.ch')
        self.assertTrue(qpartner.is_company)

    def test_import_address(self):
        """ Import an address (with dependencies) """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_address):
            import_record(self.session, 'qoqa.address',
                          self.backend_id, 4646464646)
        domain = [('qoqa_id', '=', '4646464646')]
        qaddr_ids = self.QAddress.search(cr, uid, domain)
        self.assertEquals(len(qaddr_ids), 1)
        qaddr = self.QAddress.browse(cr, uid, qaddr_ids[0])
        self.assertEquals(qaddr.name, 'Guewen Baconnier')
        self.assertEquals(qaddr.street, 'Grand Rue 3')
        self.assertEquals(qaddr.street2, '--')
        self.assertEquals(qaddr.city, 'Orbe')
        self.assertEquals(qaddr.zip, '1350')
        self.assertEquals(qaddr.country_id.id, self.ref('base.ch'))
        partner = qaddr.parent_id
        self.assertTrue(partner.is_company)

    def test_import_on_existing(self):
        """ Import a partner, should bind on an existing with same email """
        cr, uid = self.cr, self.uid
        p_id = self.Partner.create(cr, uid,
                                   {'name': 'Guewen',
                                    'email': 'guewen@gmail.com',
                                    'is_company': True})
        a_id = self.Partner.create(cr, uid,
                                   {'name': 'Guewen address 1',
                                    'parent_id': p_id})
        with mock_api_responses(qoqa_address):
            import_record(self.session, 'qoqa.address',
                          self.backend_id, 4646464646)
        domain = [('qoqa_id', '=', '4646464646')]
        qaddr_ids = self.QAddress.search(cr, uid, domain)
        self.assertEquals(len(qaddr_ids), 1)
        qaddr = self.QAddress.browse(cr, uid, qaddr_ids[0])
        partner = qaddr.parent_id
        self.assertEquals(partner.id, p_id)
        self.assertEquals(len(partner.child_ids), 2)
