# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PickingDispatchApplyCarrier(models.TransientModel):
    _inherit = 'picking.dispatch.apply.carrier'

    @api.multi
    def _check_domain(self, dispatch_ids):
        """ A domain excluding the dispatches on which we don't allow
        to change the carrier.

        Overrided to allow even the 'done' dispatches to be modified
        """
        return [('id', 'in', dispatch_ids)]
