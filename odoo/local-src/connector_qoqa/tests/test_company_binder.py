# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from contextlib import contextmanager

import openerp.tests.common as common
from openerp.addons.connector.session import ConnectorSession

from ..connector import get_environment
from ..res_company.common import CompanyBinder
from ..exception import QoQaError


class TestCompanyBinder(common.TransactionCase):
    """ Test the binding of a company.

    It is special because it expect the QoQa IDs to be manually
    setup.
    """

    def setUp(self):
        super(TestCompanyBinder, self).setUp()
        self.session = ConnectorSession.from_env(self.env)
        self.backend_record = self.env['qoqa.backend'].get_singleton()
        Company = self.env['res.company']
        vals = {'name': 'Company for tests',
                }
        self.company = Company.create(vals)

    @contextmanager
    def company_binder(self):
        backend = self.backend_record
        with get_environment(self.session, 'res.company',
                             backend.id) as conn_env:
            binder = CompanyBinder(conn_env)
            yield binder

    def test_to_openerp_id(self):
        """ Check if the OpenERP ID is found for a Company"""
        with self.company_binder() as binder:
            self.company.write({'qoqa_id': 999})
            self.assertEquals(binder.to_openerp(999),
                              self.company)

    def test_to_backend_id(self):
        """ Check if the QoQa ID is found for a Company"""
        with self.company_binder() as binder:
            self.company.write({'qoqa_id': 999})
            self.assertEquals(binder.to_backend(self.company),
                              '999')

    def test_to_openerp_id_missing(self):
        """ Check if an error is raised when the ID is missing """
        with self.company_binder() as binder:
            with self.assertRaises(QoQaError):
                binder.to_openerp(999)

    def test_to_backend_id_missing(self):
        """ Check if an error is raised when the ID is missing """
        with self.company_binder() as binder:
            with self.assertRaises(QoQaError):
                binder.to_backend(self.company)

    def test_bind_method(self):
        """ The bind method can't be used for companies """
        with self.company_binder() as binder:
            with self.assertRaises(TypeError):
                binder.bind(999, self.company)
