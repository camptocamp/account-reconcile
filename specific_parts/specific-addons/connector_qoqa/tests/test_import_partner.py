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

import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession
from ..connector import get_environment
from .common import mock_api_responses
from .data_partner import qoqa_user
from ..unit.import_synchronizer import import_record


class test_import_partner(common.TransactionCase):
    """ Test the import of partner from QoQa (actually
    QoQa Shops).
    """
    def setUp(self):
        super(test_import_partner, self).setUp()
        cr, uid = self.cr, self.uid
        backend_model = self.registry('qoqa.backend')
        self.session = ConnectorSession(cr, uid)
        self.backend_id = self.ref('connector_qoqa.qoqa_backend_config')
        # ensure we use the tested version, otherwise the response
        # of the test data would not be found
        vals = {'version': 'v1',
                'url': 'http://admin.test02.qoqa.com',
                'default_lang_id': self.ref('base.lang_en'),
                }
        backend_model.write(cr, uid, self.backend_id, vals)
        self.QPartner = self.registry('qoqa.res.partner')

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
