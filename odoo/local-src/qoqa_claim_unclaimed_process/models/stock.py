# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import api, fields, models


class StockQuantPackage(models.Model):
    """
        Crm claim
    """
    _inherit = "stock.quant.package"

    # Inverse field of stock.picking.package_ids
    @api.depends('quant_ids')
    def _compute_pickings(self):
        self.ensure_one()
        packs = self.env['stock.pack.operation'].search(
            ['|',
             ('result_package_id', '=', self.id),
             '&',
             ('product_id', '=', False),
             ('package_id', '=', self.id)])
        self.picking_ids = packs.mapped('picking_id')

    picking_ids = fields.Many2many('stock.picking',
                                   compute='_compute_pickings',
                                   string='Pickings')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_assign(self):
        # if "do_not_assign" is in context, skip method
        if self._context.get('do_not_assign', False):
            return True
        return super(StockPicking, self).action_assign()
