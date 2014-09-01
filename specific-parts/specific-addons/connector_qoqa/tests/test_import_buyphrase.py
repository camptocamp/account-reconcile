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
from .data_buyphrase import qoqa_buyphrase
from .data_metadata import qoqa_shops
from ..unit.import_synchronizer import import_record


@mock.patch('urllib2.urlopen', mock.Mock(return_value=MockResponseImage('')))
class test_import_buyphrase(QoQaTransactionCase):
    """ Test the import of buyphrase from QoQa """
    def setUp(self):
        super(test_import_buyphrase, self).setUp()
        self.Buyphrase = self.registry('qoqa.buyphrase')
        self.setUpCompany()

    def test_import_buyphrase(self):
        """ Import a Buyphrase """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_buyphrase, qoqa_shops):
            import_record(self.session, 'qoqa.buyphrase',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        buyphrase_ids = self.Buyphrase.search(cr, uid, domain)
        self.assertEquals(len(buyphrase_ids), 1)
        buyphrase = self.Buyphrase.browse(cr, uid, buyphrase_ids[0])
        self.assertEquals(buyphrase.qoqa_shop_id.qoqa_id, '100')
        self.assertEquals(buyphrase.name, 'Nickel pour le Paleo !')
        self.assertEquals(buyphrase.description,
                          "<p>Oui, c'est ici que vous devez cliquer pour "
                          "commander le produit du jour ! :)</p>")
        self.assertTrue(buyphrase.active)
        self.assertEquals(buyphrase.action, 1)
