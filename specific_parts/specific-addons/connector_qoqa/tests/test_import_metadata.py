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
from .data_metadata import qoqa_shops
from ..unit.import_synchronizer import import_batch


class test_import_metadata(common.TransactionCase):
    """ Test the import of metadata from QoQa (actually
    QoQa Shops).
    """
    def setUp(self):
        super(test_import_metadata, self).setUp()
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
        company_obj = self.registry('res.company')
        # create a new company so we'll check if it shop is linked
        # with the correct one when it is not the default one
        vals = {'name': 'Qtest', 'qoqa_id': 42}
        self.company_id = company_obj.create(cr, uid, vals)
        self.qoqa_shop_obj = self.registry('qoqa.shop')

    def test_import_shop(self):
        """ Import a Shop """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_shops):
            import_batch(self.session, 'qoqa.shop', self.backend_id)
        domain = [('qoqa_id', '=', '1')]
        shop_ids = self.qoqa_shop_obj.search(cr, uid, domain)
        self.assertEquals(len(shop_ids), 1)
        shop = self.qoqa_shop_obj.browse(cr, uid, shop_ids[0])
        self.assertEquals(shop.name, 'Qtest.ch')
        self.assertEquals(shop.company_id.id, self.company_id)
        self.assertEquals(shop.backend_id.id, self.backend_id)
