# -*- coding: utf-8 -*-
# © 2014-2016 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    state = fields.Selection(
        selection_add=[('delayed_done', 'Delayed Done')]
    )

    @api.multi
    def action_delayed_done(self):
        self.write({'state': 'delayed_done'})

    @api.model
    def _scheduler_delayed_done(self):
        """ Called from the Scheduled Actions.

        Warning: it commits after each batch so it should not be
        called outside of the scheduled actions
        """
        batches = self.search([('state', '=', 'delayed_done')])
        for batch in batches:
            try:
                batch.action_transfer()
                self.env.cr.commit()
            except:
                self.env.cr.rollback()
                _logger.exception(
                    'Could not set batch picking with ID %s as done',
                    batch
                )
