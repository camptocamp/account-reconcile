# © 2014-2016 Camptocamp SA (Damien Crier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

import odoo.tests
from odoo import fields

from odoo.addons.account.tests.common import TestAccountReconciliationCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestScenarioReconcile(TestAccountReconciliationCommon):
    @classmethod
    def setUpClass(cls):
        super(TestScenarioReconcile, cls).setUpClass()
        cls.rec_history_obj = cls.env["mass.reconcile.history"]
        cls.mass_rec_obj = cls.env["account.mass.reconcile"]
        cls.invoice_obj = cls.env["account.move"]
        cls.bk_stmt_obj = cls.env["account.bank.statement"]
        cls.bk_stmt_line_obj = cls.env["account.bank.statement.line"]
        cls.acc_move_line_obj = cls.env["account.move.line"]
        cls.mass_rec_method_obj = cls.env["account.mass.reconcile.method"]
        cls.acs_model = cls.env["res.config.settings"]

        cls.company = cls.company_data["company"]
        cls.bank_journal = cls.company_data["default_journal_bank"]
        cls.sale_journal = cls.company_data["default_journal_sale"]
        acs_ids = cls.acs_model.search([("company_id", "=", cls.company.id)])

        values = {"group_multi_currency": True}

        if acs_ids:
            acs_ids.write(values)
        else:
            default_vals = cls.acs_model.default_get([])
            default_vals.update(values)
            acs_ids = cls.acs_model.create(default_vals)

    def test_scenario_reconcile(self):
        invoice = self.create_invoice()
        self.assertEqual("posted", invoice.state)

        receivalble_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payment
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivalble_account_id,
                "amount": 50.0,
                "journal_id": self.bank_journal.id,
            }
        )
        payment.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [(0, 0, {"name": "mass.reconcile.simple.partner"})],
            }
        )
        # call the automatic reconcilation method
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)

    def test_scenario_reconcile_currency(self):
        # create currency rate
        self.env["res.currency.rate"].create(
            {
                "name": fields.Date.today(),
                "currency_id": self.ref("base.USD"),
                "rate": 1.25,
            }
        )
        # create invoice
        invoice = self._create_invoice(
            currency_id=self.ref("base.USD"),
            date_invoice=fields.Date.today(),
            auto_validate=True,
        )
        self.assertEqual("posted", invoice.state)

        self.env["res.currency.rate"].create(
            {
                "name": fields.Date.today() - timedelta(days=3),
                "currency_id": self.ref("base.USD"),
                "rate": 2,
            }
        )
        receivable_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payment
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivable_account_id,
                "amount": 50.0,
                "currency_id": self.ref("base.USD"),
                "journal_id": self.bank_journal.id,
                "date": fields.Date.today() - timedelta(days=2),
            }
        )
        payment.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [(0, 0, {"name": "mass.reconcile.simple.partner"})],
            }
        )
        # call the automatic reconcilation method
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)

    def test_scenario_reconcile_partial(self):
        invoice1 = self.create_invoice()
        invoice1.ref = "test ref"
        # create payment
        receivable_account_id = invoice1.partner_id.property_account_receivable_id.id
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice1.partner_id.id,
                "destination_account_id": receivable_account_id,
                "amount": 500.0,
                "journal_id": self.bank_journal.id,
                "ref": "test ref",
            }
        )
        payment.action_post()
        line_payment = payment.line_ids.filtered(
            lambda l: l.account_id.id == receivable_account_id
        )
        self.assertEqual(line_payment.reconciled, False)
        invoice1_line = invoice1.line_ids.filtered(
            lambda l: l.account_id.id == receivable_account_id
        )
        self.assertEqual(invoice1_line.reconciled, False)

        # Create the mass reconcile record
        reconcile_method_vals = {
            "name": "mass.reconcile.advanced.ref",
            "write_off": 0.1,
        }
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account": receivable_account_id,
                "reconcile_method": [(0, 0, reconcile_method_vals)],
            }
        )
        mass_rec.run_reconcile()

        self.assertEqual(line_payment.amount_residual, -450.0)
        self.assertEqual(invoice1_line.reconciled, True)
        invoice2 = self._create_invoice(invoice_amount=500, auto_validate=True)
        invoice2.ref = "test ref"
        invoice2_line = invoice2.line_ids.filtered(
            lambda l: l.account_id.id == receivable_account_id
        )
        mass_rec.run_reconcile()
        self.assertEqual(line_payment.reconciled, True)
        self.assertEqual(invoice2_line.reconciled, False)

        self.assertEqual(invoice2_line.amount_residual, 50.0)

    def test_scenario_reconcile_advanced(self):
        # create invoice
        invoice = self.invoice_obj.create(
            {
                'type': 'out_invoice',
                'account_id': self.ref('account.a_recv'),
                'company_id': self.ref('base.main_company'),
                'journal_id': self.ref('account.sales_journal'),
                'partner_id': self.ref('base.res_partner_12'),
                'name': "REF001",
                'invoice_line_ids': [
                    (0, 0, {
                        'name': '[PCSC234] PC Assemble SC234',
                        'account_id': self.ref('account.a_sale'),
                        'price_unit': 1000.0,
                        'quantity': 1.0,
                        'product_id': self.ref('product.product_product_3'),
                    }
                    )
                ]
            }
        )
        # validate invoice
        invoice.action_invoice_open()
        self.assertEqual('open', invoice.state)

        # create bank_statement
        statement = self.bk_stmt_obj.create(
            {
                'balance_end_real': 0.0,
                'balance_start': 0.0,
                'date': fields.Date.today(),
                'journal_id': self.ref('account.bank_journal'),
                'line_ids': [
                    (0, 0, {
                        'amount': 1000.0,
                        'partner_id': self.ref('base.res_partner_12'),
                        'name': invoice.number,
                        'ref': "REF001",
                    })
                ]
            }
        )

        # reconcile
        line_id = None
        for l in invoice.move_id.line_ids:
            if l.account_id.id == self.ref('account.a_recv'):
                line_id = l
                break

        for statement_line in statement.line_ids:
            statement_line.process_reconciliation(
                [
                    {
                        'move_line': line_id,
                        'credit': 1000.0,
                        'debit': 0.0,
                        'name': invoice.number,
                    }
                ]
            )

        # unreconcile journal item created by previous reconciliation
        lines_to_unreconcile = self.acc_move_line_obj.search(
            [('reconciled', '=', True),
             ('statement_id', '=', statement.id)]
        )
        lines_to_unreconcile.remove_move_reconcile()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                'name': 'mass_reconcile_1',
                'account': self.ref('account.a_recv'),
                'reconcile_method': [
                    (0, 0, {
                        'name': 'mass.reconcile.advanced.ref',
                    })
                ]
            }
        )
        # call the automatic reconcilation method
        mass_rec.run_reconcile()
        self.assertEqual(
            'paid',
            invoice.state
        )

    def test_reconcile_with_writeoff(self):
        invoice = self.create_invoice()

        receivable_account_id = invoice.partner_id.property_account_receivable_id.id
        # create payment
        payment = self.env["account.payment"].create(
            {
                "partner_type": "customer",
                "payment_type": "inbound",
                "partner_id": invoice.partner_id.id,
                "destination_account_id": receivable_account_id,
                "amount": 50.1,
                "journal_id": self.bank_journal.id,
            }
        )
        payment.action_post()

        # create the mass reconcile record
        mass_rec = self.mass_rec_obj.create(
            {
                "name": "mass_reconcile_1",
                "account": invoice.partner_id.property_account_receivable_id.id,
                "reconcile_method": [
                    (
                        0,
                        0,
                        {
                            "name": "mass.reconcile.simple.partner",
                            "account_lost_id": self.company_data[
                                "default_account_expense"
                            ].id,
                            "account_profit_id": self.company_data[
                                "default_account_revenue"
                            ].id,
                            "journal_id": self.company_data["default_journal_misc"].id,
                            "write_off": 0.05,
                        },
                    )
                ],
            }
        )
        # call the automatic reconcilation method
        mass_rec.run_reconcile()
        self.assertEqual("not_paid", invoice.payment_state)
        mass_rec.reconcile_method.write_off = 0.11
        mass_rec.run_reconcile()
        self.assertEqual("paid", invoice.payment_state)
        full_reconcile = invoice.line_ids.mapped("full_reconcile_id")
        writeoff_line = full_reconcile.reconciled_line_ids.filtered(
            lambda l: l.debit == 0.1
        )
        self.assertEqual(len(writeoff_line), 1)
        self.assertEqual(
            writeoff_line.move_id.journal_id.id,
            self.company_data["default_journal_misc"].id,
        )
