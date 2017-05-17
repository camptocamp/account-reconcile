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

    original_package_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Original unclaimed package (re-use for reservation)'
    )

    @api.multi
    def action_assign(self):
        # if "do_not_assign" is in context, skip method
        if self._context.get('do_not_assign', False):
            return True
        return super(StockPicking, self).action_assign()


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def quants_get_preferred_domain(self, qty, move, ops=False, lot_id=False,
                                    domain=None, preferred_domain_list=[]):
        # If 'original_package_id' is present in picking, use
        # the package's quants.
        if move and move.picking_id and move.picking_id.original_package_id:
            package = move.picking_id.original_package_id
            domain += [('package_id', '=', package.id)]
        return super(StockQuant, self).quants_get_preferred_domain(
            qty, move, ops, lot_id, domain, preferred_domain_list)
