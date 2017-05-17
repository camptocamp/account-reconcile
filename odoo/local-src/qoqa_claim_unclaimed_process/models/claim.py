# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import api, fields, models


class CrmClaim(models.Model):
    """
        Crm claim
    """
    _inherit = "crm.claim"

    @api.multi
    def _get_formatted_create_date(self):
        for claim in self:
            claim.formatted_create_date = \
                claim.create_date.strftime('%d/%m/%Y')

    pay_by_email_url = fields.Char('Pay by e-mail URL')
    unclaimed_price = fields.Integer('Price for unclaimed return')
    formatted_create_date = fields.Char(
        compute=_get_formatted_create_date,
        store=False)
    unclaimed_package_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Original unclaimed package'
    )

    @api.model
    def _send_unclaimed_reminders(self):
        """
            Cron method to send reminders on unresponded claims
        """
        company = self.env.user.company_id
        initial_categ_id = company.unclaimed_initial_categ_id.id
        first_reminder_categ_id = company.unclaimed_first_reminder_categ_id.id
        second_reminder_categ_id = \
            company.unclaimed_second_reminder_categ_id.id
        query = """
            SELECT id
            FROM crm_claim
            WHERE categ_id = %s
            AND date <
                (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - INTERVAL '%s DAYS')
            AND id NOT IN (
                SELECT claim_id
                FROM stock_picking
                WHERE claim_id IS NOT NULL
                AND type = 'out'
            )
            AND pay_by_email_url IS NOT NULL
        """

        # Get all claims for first reminder
        self.env.cr.execute(query, (initial_categ_id, 30))
        first_remainder_claim_ids = [x[0] for x in self.env.cr.fetchall()]
        for claim in self.browse(first_remainder_claim_ids):
            """ send e-mail """
            template = self.browse_ref('qoqa_claim_unclaimed_process.'
                                       'email_template_rma_first_reminder')
            template.send_mail(claim.id)
            claim.write({'categ_id': first_reminder_categ_id})
            claim.case_close()

        # Get all claims for second reminder
        self.env.cr.execute(query, (first_reminder_categ_id, 60))
        second_remainder_ids = [x[0] for x in self.env.cr.fetchall()]
        for claim in self.browse(second_remainder_ids):
            """ send e-mail """
            template = self.browse_ref('qoqa_claim_unclaimed_process.'
                                       'email_template_rma_second_reminder')
            template.send_mail(claim.id)
            claim.write({'categ_id': second_reminder_categ_id})
            claim.case_close()

        return True
