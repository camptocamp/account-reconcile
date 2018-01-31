# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import namedtuple

import mock

from freezegun import freeze_time

from openerp.addons.connector.tests.common import mock_job_delay_to_direct
from openerp.addons.connector_qoqa.unit.importer import import_record

from .common import recorder, QoQaTransactionCase

ExpectedDiscountAccounting = namedtuple(
    'ExpectedDiscountAccounting',
    'discount_type ref amount company_id create_uid '
    'date journal_id partner_id qoqa_id'
)

ExpectedDiscountAccountingLine = namedtuple(
    'ExpectedDiscountAccountingLine',
    'debit credit account_id analytic_account_id name tax_ids transaction_ref'
)


class TestImportDiscountAccounting(QoQaTransactionCase):
    """ Test the import of discount accoutings from QoQa """

    def setUp(self):
        super(TestImportDiscountAccounting, self).setUp()
        self.DiscountAccounting = self.env['qoqa.discount.accounting']
        self.setup_company()
        self.sync_metadata()

        self.journal = self.env['account.journal'].create({
            'name': 'Test journal',
            'code': 'TEST',
            'type': 'general'})
        income_type = self.env.ref('account.data_account_type_revenue')
        expense_type = self.env.ref('account.data_account_type_expenses')
        receivable_type = self.env.ref('account.data_account_type_receivable')
        self.debit_account = self.env['account.account'].create({
            'company_id': self.company_ch.id,
            'code': 'DB',
            'name': 'Debit Account',
            'user_type_id': income_type.id,
            'reconcile': False,
        })
        self.credit_account = self.env['account.account'].create({
            'company_id': self.company_ch.id,
            'code': 'CR',
            'name': 'Credit Account',
            'user_type_id': expense_type.id,
            'reconcile': False,
        })
        self.receivable_account = self.env['account.account'].create({
            'company_id': self.company_ch.id,
            'code': 'RA',
            'name': 'Receivable Account',
            'user_type_id': receivable_type.id,
            'reconcile': True,
        })
        self.env['ir.property'].search(
            [('name', '=', 'property_account_receivable_id'),
             ('res_id', '=', False)]
        ).value_reference = "account.account,%s" % self.receivable_account.id
        liabilities_account = self.env.ref(
            'account.data_account_type_current_liabilities'
        )
        self.tax_account = self.env['account.account'].create({
            'company_id': self.company_ch.id,
            'code': 'tax',
            'name': 'Tax Account',
            'user_type_id': liabilities_account.id,
            'reconcile': False,
        })
        self.tax_8 = self.env['account.tax'].create({
            'qoqa_id': '6',
            'name': '8.0%',
            'amount_type': 'percent',
            'amount': 8.0,
            'type_tax_use': 'sale',
            'company_id': self.company_ch.id,
            'tax_group_id': self.env.ref('account.tax_group_taxes').id,
            'account_id': self.tax_account.id,
            'price_include': True,
        })
        self.journal.default_debit_account_id = self.debit_account.id
        income_type.analytic_policy = 'optional'
        self.marketing = self.env.ref('connector_qoqa.promo_type_marketing')
        self.marketing.property_journal_id = self.journal.id
        self.coupon_account = self.env['account.account'].create({
            'company_id': self.company_ch.id,
            'code': 'MK',
            'name': 'Marketing Charges Account',
            'user_type_id': income_type.id,
            'reconcile': False,
        })
        marketing_product = self.env.ref(
            'qoqa_base_data.product_product_marketing_coupon'
        )
        marketing_product.property_account_income_id = self.coupon_account.id
        self.analytic_account = self.env['account.analytic.account'].create({
            'code': 'TEST',
            'name': 'Test',
        })
        self.env['qoqa.shop'].search([]).write(
            {'analytic_account_id': self.analytic_account.id}
        )

    @freeze_time('2016-06-23 00:00:00')
    def test_import_discount_accounting_batch(self):
        from_date = '2016-06-01 00:00:00'
        self.backend_record.import_discount_accounting_from_date = from_date
        batch_job_path = ('openerp.addons.connector_qoqa.unit'
                          '.importer.import_batch')
        record_job_path = ('openerp.addons.connector_qoqa.unit'
                           '.importer.import_record')
        # execute the batch job directly and replace the record import
        # by a mock (individual import is tested elsewhere)
        cassette_name = 'test_import_discount_accounting_batch'
        with recorder.use_cassette(cassette_name) as cassette, \
                mock_job_delay_to_direct(batch_job_path), \
                mock.patch(record_job_path) as import_record_mock:
            self.backend_record.import_discount_accounting()

            self.assertEqual(len(cassette.requests), 4)
            self.assertEqual(import_record_mock.delay.call_count, 2)

    @freeze_time('2016-04-23 00:00:00')
    @recorder.use_cassette()
    def test_import_discount_accounting_promo(self):
        """ Import a discount accounting of type promo """
        import_record(self.session, 'qoqa.discount.accounting',
                      self.backend_record.id, 100000001)
        domain = [('qoqa_id', '=', '100000001')]
        discount_accounting = self.DiscountAccounting.search(domain)
        discount_accounting.ensure_one()

        expected_partner = self.env['qoqa.res.partner'].search(
            [('backend_id', '=', self.backend_record.id),
             ('qoqa_id', '=', '1000001')],
        ).openerp_id
        expected = [
            ExpectedDiscountAccounting(
                discount_type='promo',
                ref='10000001',
                amount=100,
                company_id=self.company_ch,
                create_uid=self.company_ch.connector_user_id,
                date='2016-06-27',
                journal_id=self.journal,
                partner_id=expected_partner,
                qoqa_id='100000001',
            ),
        ]
        self.assert_records(expected, discount_accounting)

        move_lines = discount_accounting.line_ids

        expected_lines = [
            ExpectedDiscountAccountingLine(
                debit=0,
                credit=100,
                account_id=self.coupon_account,
                analytic_account_id=self.analytic_account,
                name=u'Emission du bons de rabais SAV',
                tax_ids=self.env['account.tax'],
                transaction_ref="ABCD",
            ),
            ExpectedDiscountAccountingLine(
                debit=92.59,
                credit=0,
                account_id=self.debit_account,
                analytic_account_id=self.analytic_account,
                name=u'Frais service clientèle net',
                tax_ids=self.tax_8,
                transaction_ref="ABCD",
            ),
            ExpectedDiscountAccountingLine(
                debit=7.41,
                credit=0,
                account_id=self.tax_account,
                analytic_account_id=self.env['account.analytic.account'],
                name=u'Frais service clientèle net 8.0%',
                tax_ids=self.env['account.tax'],
                transaction_ref=False,
            ),
        ]
        self.assert_records(expected_lines, move_lines)

    @freeze_time('2016-04-23 00:00:00')
    @recorder.use_cassette()
    def test_import_discount_accounting_voucher(self):
        """Import a discount accounting of type voucher: skipped

        The import of voucher issuances is deprecated.
        """
        # the import should do nothing
        import_record(self.session, 'qoqa.discount.accounting',
                      self.backend_record.id, 100000002)

        domain = [('qoqa_id', '=', '100000002')]
        discount_accounting = self.DiscountAccounting.search(domain)
        self.assertFalse(discount_accounting)
