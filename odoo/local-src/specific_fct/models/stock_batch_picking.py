# -*- coding: utf-8 -*-
# © 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp import api


class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    active = fields.Boolean(
        'Active',
        default=True,
        index=True,
        help="The active field allows you to hide the picking dispatch "
             "without removing it."
    )

    @api.multi
    def action_transfer(self):
        """
            Force the qty_done to always be equal to product_qty with
            force_qty=True in force_transfert
        """
        batches = self.get_not_empties()
        for batch in batches:
            if not batch.verify_state():
                batch.active_picking_ids.force_transfer(
                    force_qty=True
                )
