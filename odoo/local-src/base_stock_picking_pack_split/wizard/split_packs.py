# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import _, api, fields, models


class PickingSplitPacks(models.TransientModel):
    _name = 'picking.split.packs'

    qty_per_pack = fields.Integer(
        'Number of product per pack',
        required=True,
        default=1,
        help="Defines the maximum number of product in a pack. "
             "We consider each product of the packing has the same size.")

    _sql_constraints = [
        ('qty_per_pack_number', 'CHECK (qty_per_pack > 0)',
         'The number of products per pack must be above 0.'),
    ]

    @api.multi
    def _split_packs(self, pickings):
        """ Fill packs with products

        We consider that all product have the same size

        """
        pickings.prepare_packs(max_qty=self.qty_per_pack)
        return pickings.mapped('pack_operation_product_ids.result_package_id')

    @api.multi
    def split_packs(self):
        self.ensure_one()
        ctx = self.env.context
        assert ctx.get('active_ids'), "'active_ids' required"
        picking_ids = ctx['active_ids']
        pickings = self.env['stock.picking'].browse(picking_ids)

        packs = self._split_packs(pickings)

        return {
            'domain': "[('id', 'in', %s)]" % packs.ids,
            'name': _('Generated Packs'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.quant.package',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
