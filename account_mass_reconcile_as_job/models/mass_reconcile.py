# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import ast
import logging

_logger = logging.getLogger(__name__)

from odoo import api, models
try:
    from odoo.addons.queue_job.job import job
except ImportError:
    _logger.debug('Can not `import queue_job`.')


class AccountMassReconcile(models.Model):
    _inherit = 'account.mass.reconcile'

    @api.multi
    def run_reconcile(self):
        as_job = self.env['ir.config_parameter'].sudo().get_param(
            'account.mass.reconcile.as.job', default=False
        )
        try:
            as_job = ast.literal_eval(as_job) if as_job else False
        except ValueError:
            as_job = False

        for rec in self:
            if as_job and self.env.context.get('mass_reconcile_as_job', True):
                self.with_delay().reconcile_as_job()
                return True
            else:
                return super(AccountMassReconcile, rec).run_reconcile()

    @job(default_channel='root.mass_reconcile')
    def reconcile_as_job(self):
        """Run reconciliation with appropriate context key to interapt new job
        creation"""
        self.with_context(mass_reconcile_as_job=False).run_reconcile()
