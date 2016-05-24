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

from .common import mock_api_responses, QoQaTransactionCase
from .data_voucher import qoqa_voucher
from ..unit.import_synchronizer import import_record


@unittest2.skip("Not implemented yet")
class test_import_voucher(QoQaTransactionCase):
    """ Test the import of order from QoQa  """

    def setUp(self):
        super(test_import_voucher, self).setUp()
        self.QVoucher = self.registry('')

    def test_import_voucher(self):
        """ Import a voucher """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_voucher):
            import_record(self.session, '',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        qvoucher_ids = self.QVoucher.search(cr, uid, domain)
        self.assertEquals(len(qvoucher_ids), 1)
