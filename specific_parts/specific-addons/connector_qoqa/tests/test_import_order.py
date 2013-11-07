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
import unittest2

from openerp.addons.connector.session import ConnectorSession
from .common import mock_api_responses, QoQaTransactionCase
from .data_order import qoqa_order
from .data_partner import qoqa_user, qoqa_address
from .data_offer import qoqa_offer
from ..unit.import_synchronizer import import_record


@unittest2.skip("Not implemented yet")
class test_import_order(QoQaTransactionCase):
    """ Test the import of order from QoQa  """

    def setUp(self):
        super(test_import_order, self).setUp()
        self.QSale = self.registry('qoqa.sale.order')

    def test_import_order(self):
        """ Import a sales order """
        cr, uid = self.cr, self.uid
        data = qoqa_order, qoqa_product, qoqa_offer, qoqa_user, qoqa_address
        with mock_api_responses(*data):
            import_record(self.session, 'qoqa.sale.order',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        qsale_ids = self.QSale.search(cr, uid, domain)
        self.assertEquals(len(qsale_ids), 1)
        qsale = self.QSale.browse(cr, uid, qsale_ids[0])
