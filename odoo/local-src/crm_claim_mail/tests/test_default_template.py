# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import openerp.tests.common as test_common


class TestDefaultTemplate(test_common.TransactionCase):

    def test_mail_compose_crm_claim(self):
        ctx = {'default_model': 'crm.claim'}
        composer = self.MailComposer.with_context(ctx).create({})
        self.assertEquals(composer.template_id, self.crm_template)

    def test_mail_compose_partner(self):
        ctx = {'default_model': 'res.partner'}
        composer = self.MailComposer.with_context(ctx).create({})
        self.assertFalse(composer.template_id)

    def setUp(self):
        super(TestDefaultTemplate, self).setUp()
        self.MailComposer = self.env['mail.compose.message']
        model = self.env.ref('crm_claim.model_crm_claim')
        self.crm_template = self.env['mail.template'].create({
            'name': "Template crm_claim",
            'model_id': model.id,
            'is_default': True
            })
