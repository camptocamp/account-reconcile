# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

# ignore errors for odoo's code copy-pasted
# flake8: noqa: E127,E124

from openerp import models
from openerp.tools import float_round


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    # full override of the method, because it generates an unoptimized
    # query.
    def get_reconciliation_proposition(self, excluded_ids=None):
        """ Returns move lines that constitute the best guess to reconcile a
        statement line Note: it only looks for move lines in the same currency
        as the statement line.
        """
        self.ensure_one()
        if not excluded_ids:
            excluded_ids = []
        amount = self.amount_currency or self.amount
        company_currency = self.journal_id.company_id.currency_id
        st_line_currency = self.currency_id or self.journal_id.currency_id
        currency = (st_line_currency and st_line_currency != company_currency) and st_line_currency.id or False
        precision = st_line_currency and st_line_currency.decimal_places or company_currency.decimal_places
        params = {'company_id': self.env.user.company_id.id,
                    'account_payable_receivable': (self.journal_id.default_credit_account_id.id, self.journal_id.default_debit_account_id.id),
                    'amount': float_round(amount, precision_digits=precision),
                    'partner_id': self.partner_id.id,
                    'excluded_ids': tuple(excluded_ids),
                    'ref': self.name,
                    }
        # Look for structured communication match
        if self.name:
            # XXX LOCAL CHANGES HERE
            sql_query = self._get_proposition_query_by_name(
                excluded_ids=excluded_ids
            )
            # XXX END OF LOCAL CHANGES
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.fetchone()
            if results:
                return self.env['account.move.line'].browse(results[0])

        # Look for a single move line with the same amount
        field = currency and 'amount_residual_currency' or 'amount_residual'
        liquidity_field = currency and 'amount_currency' or amount > 0 and 'debit' or 'credit'
        liquidity_amt_clause = currency and '%(amount)s' or 'abs(%(amount)s)'
        sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
                " AND ("+field+" = %(amount)s OR (acc.internal_type = 'liquidity' AND "+liquidity_field+" = " + liquidity_amt_clause + ")) \
                ORDER BY date_maturity asc, aml.id asc LIMIT 1"
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.fetchone()
        if results:
            return self.env['account.move.line'].browse(results[0])

        return self.env['account.move.line']

    def _get_proposition_query_by_name(self, excluded_ids=None):
        (select_clause,
            from_clause,
            where_clause) = self._get_common_sql_query(
                overlook_partner=True,
                excluded_ids=excluded_ids,
                split=True)
        # this is the optimized query
        query = """
        SELECT t.id,
               t.date_maturity,
               CASE WHEN l.ref = %%(ref)s THEN 1 ELSE 2 END AS temp_field_order
        FROM (
            %(select)s, aml.date_maturity
            %(from)s
            %(where)s
            AND aml.ref= %%(ref)s
            UNION
            %(select)s, aml.date_maturity
            %(from)s
            JOIN account_move m ON m.id = aml.move_id
            %(where)s
            AND m.name = %%(ref)s
            ) as t
        INNER JOIN account_move_line l
        ON l.id = t.id
        ORDER BY
            temp_field_order,
            t.date_maturity ASC,
            t.id ASC;
        """
        parts = {'select': select_clause,
                 'from': from_clause,
                 'where': where_clause}
        return query % parts
