# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PickingBatchApplyCarrier(models.TransientModel):
    _inherit = 'picking.batch.apply.carrier'

    @api.multi
    def _check_domain(self, batch_ids):
        """ A domain excluding the batches on which we don't allow
        to change the carrier.

        Overrided to allow even the 'done' batches to be modified
        """
        return [('id', 'in', batch_ids)]
