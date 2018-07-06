# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from collections import defaultdict

from openerp import api, fields, models


class StockQuantPackage(models.Model):
    """
        Crm claim
    """
    _inherit = "stock.quant.package"

    # Inverse field of stock.picking.package_ids
    @api.depends('quant_ids')
    def _compute_pickings(self):
        for package in self:
            packs = package.env['stock.pack.operation'].search([
                '|',
                ('result_package_id', '=', package.id),
                '&',
                ('product_id', '=', False),
                ('package_id', '=', package.id),
            ])
            package.picking_ids = packs.mapped('picking_id')

    picking_ids = fields.Many2many('stock.picking',
                                   compute='_compute_pickings',
                                   string='Pickings')

    @api.multi
    def unpack(self):
        package_data = defaultdict(dict)
        for package in self:
            pack_id = package.id
            pickings = package.picking_ids.filtered(
                lambda x: x.state not in ['done', 'cancel']
            )
            if not pickings:
                continue
            product_dict = defaultdict(dict)
            for quant in package.quant_ids:
                product_dict[quant.product_id.id].update({
                    'qty': quant.qty + product_dict[
                        quant.product_id.id
                    ].get('qty', 0),
                    'uom': quant.product_id.uom_id.id,
                    'name': quant.product_id.partner_ref,
                })
            package_data[pack_id]['data'] = product_dict
            package_data[pack_id]['pickings'] = pickings.ids
        res = super(StockQuantPackage, self).unpack()
        self.unlink()
        self.env["stock.picking"]._get_items_from_unpack(package_data)
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    original_package_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Original unclaimed package (re-use for reservation)'
    )

    @api.model
    def _get_items_from_unpack(self, package_data):
        for pack_id, items in package_data.iteritems():
            pickings = self.browse(items['pickings'])
            for picking in pickings:
                picking.pack_operation_pack_ids.filtered(
                    lambda x: x.package_id.id in (pack_id, False)
                ).unlink()
                move_lines = [
                    (0, 0, {
                        'product_id': x,
                        'name': y.get('name', ''),
                        'product_uom_qty': y.get('qty', 0),
                        'product_uom': y.get('uom', False),
                        'location_id': picking.location_id.id,
                        'location_dest_id': picking.location_dest_id.id,
                    })
                    for x, y in items['data'].iteritems()
                ]
                picking.update({
                    'move_lines': move_lines,
                })
            pickings.do_unreserve()
            for picking in pickings:
                if picking.move_lines:
                    picking.action_assign()
            pickings.invalidate_cache()

    @api.multi
    def action_assign(self):
        # if "do_not_assign" is in context, skip method
        if self._context.get('do_not_assign', False):
            # can still be draft... if so, action_confirm
            if self.state == 'draft':
                self.action_confirm()
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
