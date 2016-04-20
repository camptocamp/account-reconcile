# -*- coding: utf-8 -*-
# © 2014-2016 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import _, api, models
from openerp.exceptions import UserError


class PickingDispatchDelayDone(models.TransientModel):
    _name = 'picking.dispatch.delayed.done'
    _description = 'Picking Dispatch Delayed Done'

    @api.multi
    def delayed_done(self):
        dispatch_ids = self.env.context.get('active_ids')
        if not dispatch_ids:
            raise UserError(_('No selected picking dispatch'))

        dispatches = self.env['picking.dispatch'].search([
            ('state', '=', 'progress'),
            ('id', 'in', dispatch_ids)
        ])
        if len(dispatches) != len(dispatch_ids):
            raise UserError(
                _('All the picking dispatches must be in progress '
                  'to be set to done.')
            )
        dispatches.action_delayed_done()
