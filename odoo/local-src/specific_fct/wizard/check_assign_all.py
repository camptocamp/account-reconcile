# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PickingBatchApplyCarrier(models.TransientModel):
    _inherit = 'stock.picking.check.assign.all'

    check_availability = fields.Boolean(default=False)
    force_availability = fields.Boolean(default=False)
    process_picking = fields.Boolean(default=False)
