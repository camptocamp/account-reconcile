# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, tools


class AccountMoveLinesReconciledReport(models.Model):
    _name = 'account.move.reconciled.report'
    _auto = False

    account_move_id = fields.Many2one('account.move.line',
                                      string="Account move")

    @api.model_cr
    def init(self):
        """Select lines which violate defined rules"""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """CREATE OR REPLACE VIEW %s AS (
                    WITH CTE AS (
                    SELECT  daml.id daml_id, caml.id caml_id, pr.id
                    FROM account_partial_reconcile  pr
                    LEFT JOIN account_move_line daml
                        ON daml.id = pr.debit_move_id
                    LEFT JOIN account_move_line caml
                        ON caml.id = pr.credit_move_id
                    LEFT JOIN account_account daa ON daa.id = daml.account_id
                    LEFT JOIN account_account caa ON caa.id = caml.account_id
                    LEFT JOIN account_account_type daat
                        ON daa.user_type_id = daat.id
                    LEFT JOIN account_account_type caat
                        ON caa.user_type_id = caat.id
                    WHERE (daat.type in ('receivable', 'payable')
                    OR caat.type in ('receivable', 'payable'))
                    AND (daml.partner_id <> caml.partner_id
                    OR (daml.partner_id IS NULL
                        AND caml.partner_id IS NOT NULL)
                    OR (caml.partner_id IS NULL
                        AND daml.partner_id IS NOT NULL))
                )
                    SELECT CTE.daml_id as id,
                        CTE.daml_id as account_move_id  FROM CTE
                UNION
                    SELECT CTE.caml_id as id,
                        CTE.caml_id as account_move_id  FROM CTE
                UNION
                    SELECT faml.id as id,
                        faml.id as account_move_id
                        FROM account_move_line faml
                        LEFT JOIN account_full_reconcile fr
                            ON faml.full_reconcile_id = fr.id
                        LEFT JOIN account_move_line saml
                            ON saml.full_reconcile_id = fr.id
                        JOIN account_account faa ON faa.id = faml.account_id
                        JOIN account_account saa ON saa.id = saml.account_id
                        JOIN account_account_type faat
                            ON faa.user_type_id = faat.id
                        JOIN account_account_type saat
                            ON saa.user_type_id = saat.id
                        WHERE (faat.type in ('receivable', 'payable')
                        OR saat.type in ('receivable', 'payable'))
                        AND faml.id <> saml.id
                        AND (faml.partner_id <> saml.partner_id
                        OR (faml.partner_id IS NULL
                            AND saml.partner_id IS NOT NULL)
                        OR (saml.partner_id IS NULL
                            AND faml.partner_id IS NOT NULL))
            )
        """
            % self._table
        )
