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
from ..res_company import CompanyBinder
from ..exception import QoQaError


class test_company_binder(common.TransactionCase):
    """ Test the binding of a company.

    It is special because it expect the QoQa IDs to be manually
    setup.
    """

    def setUp(self):
        super(test_company_binder, self).setUp()
        cr, uid = self.cr, self.uid
        backend_model = self.registry('qoqa.backend')
        self.session = ConnectorSession(cr, uid)
        backend_id = self.ref('connector_qoqa.qoqa_backend_config')
        company_obj = self.registry('res.company')
        vals = {'name': 'Company for tests',
                }
        company_id = company_obj.create(cr, uid, vals)
        self.company = company_obj.browse(cr, uid, company_id)
        environment = get_environment(self.session, 'res.company', backend_id)
        self.binder = CompanyBinder(environment)

    def test_to_openerp_id(self):
        """ Check if the OpenERP ID is found for a Company"""
        self.company.write({'qoqa_id': 999})
        self.assertEquals(self.binder.to_openerp(999),
                          self.company.id)

    def test_to_backend_id(self):
        """ Check if the QoQa ID is found for a Company"""
        self.company.write({'qoqa_id': 999})
        self.assertEquals(self.binder.to_backend(self.company.id),
                          '999')

    def test_to_openerp_id_missing(self):
        """ Check if an error is raised when the ID is missing """
        with self.assertRaises(QoQaError):
            self.binder.to_openerp(999)

    def test_to_backend_id_missing(self):
        """ Check if an error is raised when the ID is missing """
        with self.assertRaises(QoQaError):
            self.binder.to_backend(self.company.id)

    def test_bind_method(self):
        """ The bind method can't be used for companies """
        with self.assertRaises(TypeError):
            self.binder.bind(999, self.company.id)
