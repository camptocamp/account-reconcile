# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import namedtuple

import mock

from freezegun import freeze_time

from openerp.addons.connector.tests.common import mock_job_delay_to_direct
from openerp.addons.connector_qoqa.unit.importer import import_record

from .common import recorder, QoQaTransactionCase

ExpectedClaim = namedtuple(
    'ExpectedClaim',
    'name description qoqa_shop_id user_id team_id warehouse_id '
    'partner_id email_from partner_phone invoice_id'
)

ExpectedMedium = namedtuple(
    'ExpectedMedium',
    'name type url'
)


class TestImportClaim(QoQaTransactionCase):
    """ Test the import of Claims from QoQa.  """

    def setUp(self):
        super(TestImportClaim, self).setUp()
        self.QoqaClaim = self.env['qoqa.crm.claim']
        self.Claim = self.env['crm.claim']
        self.setup_company()
        self.sync_metadata()
        self.shop = self.env['qoqa.shop'].search([('name', '=', 'Qwine')])
        self.user = self.env.ref('base.user_demo')
        self.team = self.env['crm.team'].create({'name': 'Team'})
        self.warehouse = self.env['stock.warehouse'].search([], limit=1)
        alias_defaults = {
            'qoqa_shop_id': self.shop.id,
            'user_id': self.user.id,
            'team_id': self.team.id,
            'warehouse_id': self.warehouse.id,
        }
        crm_claim_model_model = self.env['ir.model'].search(
            [('model', '=', 'crm.claim')],
            limit=1,
        )
        self.env['mail.alias'].create({
            'alias_name': 'test.qoqa',
            'alias_model_id': crm_claim_model_model.id,
            'alias_contact': 'everyone',
            'alias_defaults': unicode(alias_defaults),
        })

    @freeze_time('2016-06-27 00:00:00')
    def test_import_claim_batch(self):
        """ Import a batch of claims """
        from_date = '2016-06-01 00:00:00'
        self.backend_record.import_crm_claim_from_date = from_date
        batch_job_path = ('openerp.addons.connector_qoqa.unit'
                          '.importer.import_batch')
        record_job_path = ('openerp.addons.connector_qoqa.unit'
                           '.importer.import_record')
        # execute the batch job directly and replace the record import
        # by a mock (individual import is tested elsewhere)
        with recorder.use_cassette('test_import_crm_claim_batch') as cassette,\
                mock_job_delay_to_direct(batch_job_path), \
                mock.patch(record_job_path) as import_record_mock:
            self.backend_record.import_crm_claim()

            self.assertEqual(len(cassette.requests), 4)
            self.assertEqual(import_record_mock.delay.call_count, 2)

    def _create_qoqa_sale_order(self, partner):
        product = self.env['product.product'].create({'name': 'Test'})
        sale = self.env['sale.order'].create({
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'order_line': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 5.0,
                'product_uom': product.uom_id.id,
            })],
            'pricelist_id': self.env.ref('product.list0').id,
        })
        return sale

    def _create_partner(self):
        partner = self.env['res.partner'].create({
            'name': 'Admin',
            'phone': '0041 79 123 45 67',
        })
        return partner

    @freeze_time('2016-04-27 00:00:00')
    def test_import_claim_record(self):
        """ Import a claim """
        partner = self._create_partner()
        self.create_bindind_no_export(
            'qoqa.res.partner',
            partner.id,
            qoqa_id='1000001'
        )
        sale = self._create_qoqa_sale_order(partner)
        sale.action_confirm()
        sale.action_invoice_create()
        self.create_bindind_no_export(
            'qoqa.sale.order',
            sale.id,
            qoqa_id=2,
        )
        with recorder.use_cassette('test_import_claim_record_4'):
            import_record(self.session, 'qoqa.crm.claim',
                          self.backend_record.id, 4)
        domain = [('qoqa_id', '=', '4')]
        claim_binding = self.QoqaClaim.search(domain)
        claim_binding.ensure_one()

        expected_description = (
            u"<pre>Bonjour, J'ai enfin reçu mon iPhone. "
            u"Mais il était cassé dans "
            u"sa boite. Vous pouvez voir les cassures dans la photo envoyé. "
            u"Comme tout ça à pas l'air très solide je vais reprendre "
            u"mon 3310 merci\n</pre>"
        )
        expected = [
            ExpectedClaim(
                name=u'Admin - Order <150414-C8TBCI>',
                description=expected_description,
                qoqa_shop_id=self.shop,
                user_id=self.user,
                team_id=self.team,
                warehouse_id=self.warehouse,
                partner_id=partner,
                email_from='dev@qoqa.com',  # from API
                partner_phone='0041 79 123 45 67',   # from onchange
                invoice_id=sale.invoice_ids,
            )]

        self.assert_records(expected, claim_binding)
        lines = claim_binding.claim_line_ids

        # check that we don't re-create the lines when we import again:
        self.assertTrue(claim_binding.claim_line_ids)
        with recorder.use_cassette('test_import_claim_record_4'):
            import_record(self.session, 'qoqa.crm.claim',
                          self.backend_record.id, 4)

        self.assert_records(expected, claim_binding)
        self.assertEquals(lines, claim_binding.claim_line_ids)

        attachment = self.env['ir.attachment'].search(
            [('res_id', '=', claim_binding.openerp_id.id),
             ('res_model', '=', 'crm.claim')],
        )
        self.assertEquals(len(attachment), 1)
        url = ('https://s3-eu-central-1.amazonaws.com/qoqa4-sprint/'
               'cs/claim_media/files/000/000/002/original/'
               'iphone-5s-front.jpg?1467030479')
        expected = [
            ExpectedMedium(
                name=u'iphone-5s-front.jpg?1467030479',
                url=url,
                type='url',
            )
        ]
        self.assert_records(expected, attachment)
