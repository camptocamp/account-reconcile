# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, tools


class AccountReconcilePartnerMismatchReport(models.Model):
    _name = 'account.reconcile.partner.mismatch.report'
    _auto = False

    partial_reconcile_id = fields.Many2one(
        'account.partial.reconcile',
        string="Partial Reconcile"
    )
    full_reconcile_id = fields.Many2one('account.full.reconcile')
    debit_move_id = fields.Many2one('account.move.line', string="Debit move")
    debit_amount = fields.Float("Debit amount")
    debit_partner_id = fields.Many2one('res.partner', string="Debit partner")
    debit_account_id = fields.Many2one(
        'account.account',
        string="Debit account"
    )
    debit_account_type_id = fields.Many2one(
        'account.account.type',
        string="Debit account type",
    )
    credit_move_id = fields.Many2one('account.move.line', string="Credit move")
    credit_amount = fields.Float("Credit amount")
    credit_partner_id = fields.Many2one('res.partner', string="Credit partner")
    credit_account_id = fields.Many2one(
        'account.account',
        string="Credit account"
    )
    credit_account_type_id = fields.Many2one(
        'account.account.type',
        string="Credit account type",
    )

    @api.model_cr
    def init(self):
        """Select lines which violate defined rules"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
                    SELECT pr.id id
                    , pr.id partial_reconcile_id
                    , pr.full_reconcile_id
                    , pr.debit_move_id
                    , daml.debit debit_amount
                    , daat.id debit_account_type_id
                    , daml.partner_id debit_partner_id
                    , daml.account_id debit_account_id
                    , pr.credit_move_id
                    , caml.credit credit_amount
                    , caat.id credit_account_type_id
                    , caml.partner_id credit_partner_id
                    , caml.account_id credit_account_id
                    FROM account_partial_reconcile  pr
                    LEFT JOIN account_move_line daml
                        ON daml.id = pr.debit_move_id
                    LEFT JOIN account_move_line caml
                        ON caml.id = pr.credit_move_id
                    LEFT JOIN account_account_type daat
                        ON daml.user_type_id = daat.id
                    LEFT JOIN account_account_type caat
                        ON caml.user_type_id = caat.id
                    WHERE (daat.type in ('receivable', 'payable')
                    OR caat.type in ('receivable', 'payable'))
                    AND (daml.partner_id <> caml.partner_id
                    OR (daml.partner_id IS NULL
                        AND caml.partner_id IS NOT NULL)
                    OR (caml.partner_id IS NULL
                        AND daml.partner_id IS NOT NULL))
                )
        """
            % self._table
        )
