# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import exceptions

from .common import recorder, QoQaTransactionCase, secrets


class TestAuth(QoQaTransactionCase):

    @recorder.use_cassette
    def test_auth_success(self):
        AuthWizard = self.env['qoqa.backend.auth']
        wizard = AuthWizard.with_context(
            active_model='qoqa.backend',
            active_id=self.backend_record.id
        ).create({
            'login': secrets.login,
            'password': secrets.password,
        })
        wizard.auth()
        self.assertTrue(self.backend_record.token)

    @recorder.use_cassette
    def test_auth_failure(self):
        AuthWizard = self.env['qoqa.backend.auth']
        wizard = AuthWizard.with_context(
            active_model='qoqa.backend',
            active_id=self.backend_record.id
        ).create({
            'login': 'wrong_user',
            'password': 'wrong_password',
        })
        with self.assertRaises(exceptions.UserError):
            wizard.auth()
