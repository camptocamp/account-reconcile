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
from .data_product import qoqa_product
from ..unit.import_synchronizer import import_record


class test_import_product(QoQaTransactionCase):
    """ Test the import of product from QoQa (actually
    QoQa Shops).
    """
    def setUp(self):
        super(test_import_product, self).setUp()
        self.QTemplate = self.registry('qoqa.product.template')
        self.QVariant = self.registry('qoqa.product.product')

    def test_import_template(self):
        """ Import a template """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_product):
            import_record(self.session, 'qoqa.product.template',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        qtemplate_ids = self.QTemplate.search(cr, uid, domain)
        self.assertEquals(len(qtemplate_ids), 1)
        qtemplate = self.QTemplate.browse(cr, uid, qtemplate_ids[0])
        self.assertEquals(qtemplate.name, 'All Star Mid')


    def test_import_variant(self):
        """ Import a variant """
        cr, uid = self.cr, self.uid
        with mock_api_responses(qoqa_product):
            import_record(self.session, 'qoqa.product.product',
                          self.backend_id, 99999999)
        domain = [('qoqa_id', '=', '99999999')]
        qvariant_ids = self.QVariant.search(cr, uid, domain)
        self.assertEquals(len(qvariant_ids), 1)
        qvariant = self.QVariant.browse(cr, uid, qvariant_ids[0])
        self.assertEquals(qvariant.default_code, '5259.22')
