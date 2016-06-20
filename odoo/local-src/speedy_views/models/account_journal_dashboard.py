# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# Copyright 2016 Odoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from datetime import datetime

from openerp import models, api, _
from openerp.tools.misc import formatLang


class account_journal(models.Model):
    _inherit = "account.journal"

    # WARNING: the following methods are totally overidded from
    # 'account/models/account_journal_dashboard.py'
    # to optimize the loading of the dashboard

    @api.multi
    def get_line_graph_datas(self):
        return [{'values': []}]

    @api.multi
    def get_bar_graph_datas(self):
        return [{'values': []}]

    @api.multi
    def get_journal_dashboard_datas(self):
        currency = self.currency_id or self.company_id.currency_id
        number_to_reconcile = last_balance = 0
        title = ''
        number_draft = number_waiting = number_late = 0
        sum_draft = sum_waiting = sum_late = 0
        if self.type in ['bank', 'cash']:
            last_bank_stmt = self.env['account.bank.statement'].search(
                [('journal_id', 'in', self.ids)],
                order="date desc, id desc",
                limit=1
            )
            last_balance = (last_bank_stmt[0].balance_end if
                            last_bank_stmt else 0)
            # <--- replaced ORM by the following query, which is far more quick
            query = ("SELECT count(sl.id) FROM account_bank_statement_line sl "
                     "INNER JOIN account_bank_statement s "
                     "ON s.id = sl.statement_id "
                     "WHERE s.journal_id IN %s "
                     "AND s.state = %s "
                     "AND NOT EXISTS (SELECT id FROM account_move m "
                     "                WHERE m.statement_line_id = sl.id) "
                     )
            self.env.cr.execute(query, (tuple(self.ids), 'open'))
            number_to_reconcile = self.env.cr.fetchone()[0]
            # <--- Removed computation of "account_balance", cause
            # it was long to compute and not very useful
        # this comment is copied from the original method (sic):
        # TODO need to check if all invoices are in the same currency than the
        # journal!!!!
        elif self.type in ['sale', 'purchase']:
            title = (_('Bills to pay') if self.type == 'purchase'
                     else _('Invoices owed to you'))
            # optimization to find total and sum of invoice that are in draft,
            # open state
            query = ("SELECT state, amount_total, currency_id AS currency "
                     "FROM account_invoice WHERE journal_id = %s "
                     "AND state NOT IN ('paid', 'cancel');")
            self.env.cr.execute(query, (self.id,))
            query_results = self.env.cr.dictfetchall()
            today = datetime.today()
            query = ("SELECT amount_total, currency_id AS currency "
                     "FROM account_invoice "
                     "WHERE journal_id = %s AND date < %s AND state = 'open';")
            self.env.cr.execute(query, (self.id, today))
            late_query_results = self.env.cr.dictfetchall()
            sum_draft = 0.0
            number_draft = 0
            number_waiting = 0
            for result in query_results:
                cur = self.env['res.currency'].browse(result.get('currency'))
                if result.get('state') in ['draft', 'proforma', 'proforma2']:
                    number_draft += 1
                    sum_draft += cur.compute(result.get('amount_total'),
                                             currency)
                elif result.get('state') == 'open':
                    number_waiting += 1
                    sum_waiting += cur.compute(result.get('amount_total'),
                                               currency)
            sum_late = 0.0
            number_late = 0
            for result in late_query_results:
                cur = self.env['res.currency'].browse(result.get('currency'))
                number_late += 1
                sum_late += cur.compute(result.get('amount_total'), currency)

        last_balance = formatLang(
            self.env, last_balance,
            currency_obj=self.currency_id or self.company_id.currency_id
        )
        sum_draft = formatLang(
            self.env,
            sum_draft or 0.0,
            currency_obj=self.currency_id or self.company_id.currency_id
        )
        sum_waiting = formatLang(
            self.env, sum_waiting or 0.0,
            currency_obj=self.currency_id or self.company_id.currency_id
        )
        sum_late = formatLang(
            self.env, sum_late or 0.0,
            currency_obj=self.currency_id or self.company_id.currency_id
        )
        return {
            'number_to_reconcile': number_to_reconcile,
            'account_balance': 0,
            'last_balance': last_balance,
            'number_draft': number_draft,
            'number_waiting': number_waiting,
            'number_late': number_late,
            'sum_draft': sum_draft,
            'sum_waiting': sum_waiting,
            'sum_late': sum_late,
            'currency_id': currency.id,
            'bank_statements_source': self.bank_statements_source,
            'title': title,
        }
