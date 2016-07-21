# -*- coding: utf-8 -*-
# © 2014-2016 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import _, api, models
from openerp.exceptions import UserError


class StockBatchPickingDelayDone(models.TransientModel):
    _name = 'stock.batch.picking.delayed.done'
    _description = 'Batch Picking Delayed Done'

    @api.multi
    def delayed_done(self):
        batches_id = self.env.context.get('active_ids')
        if not batches_id:
            raise UserError(_('No selected batch picking'))

        batches = self.env['stock.batch.picking'].search([
            ('state', 'in', ['draft', 'assigned']),
            ('id', 'in', batches_id)
        ])
        if len(batches) != len(batches_id):
            raise UserError(
                _('All the batches must be draft or assigned '
                  'to be set to done.')
            )
        batches.action_delayed_done()
