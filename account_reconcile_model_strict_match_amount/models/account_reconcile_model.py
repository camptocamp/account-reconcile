# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class AccountReconcileModel(models.Model):

    _inherit = 'account.reconcile.model'

    strict_match_total_amount = fields.Boolean(
        string="Strict Amount Matching",
        help="Avoid bypassing the Amount Matching parameter in case of a "
             "statement line communication matching exactly existing entries."
    )

    @api.multi
    def _get_select_communication_flag(self):
        if not self.match_total_amount or not self.strict_match_total_amount:
            return super()._get_select_communication_flag()
        else:
            return '''
                -- Determine a matching or not with the statement line communication using the move.name or move.ref.
                -- only digits are considered and reference are split by any space characters
                COALESCE(
                    regexp_split_to_array(substring(REGEXP_REPLACE(move.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'), '\s+')
                    && regexp_split_to_array(substring(REGEXP_REPLACE(st_line.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'), '\s+')
                    OR
                    (
                        move.ref IS NOT NULL
                        AND
                            regexp_split_to_array(substring(REGEXP_REPLACE(move.ref, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'), '\s+')
                            &&
                            regexp_split_to_array(substring(REGEXP_REPLACE(st_line.name, '[^0-9|^\s]', '', 'g'), '\S(?:.*\S)*'), '\s+')
                ), TRUE)
                AND
                CASE
                    WHEN abs(st_line.amount) < abs(aml.balance) THEN st_line.amount / aml.balance * 100
                    WHEN abs(st_line.amount) > abs(aml.balance) THEN aml.balance / st_line.amount * 100
                    ELSE 100
                END >= %s AS communication_flag
            ''' % self.match_total_amount_param
