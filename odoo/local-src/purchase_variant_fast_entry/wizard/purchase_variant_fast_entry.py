# -*- coding: utf-8 -*-
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class PurchaseVariantFastEntry(models.TransientModel):
    _name = 'purchase.variant.fast.entry'
    _description = 'Fast entry of variants in purchase orders'

    product_tmpl_id = fields.Many2one(comodel_name='product.template',
                                      string='Product Template',
                                      required=True)
    quantity = fields.Float(
        string='Default quantity',
        digits_compute=dp.get_precision('Product Unit of Measure')
    )

    @api.multi
    def _prepare_line(self, purchase, variant):
        purchase_line_model = self.env['purchase.order.line']
        line = purchase_line_model.new({
            'order_id': purchase.id,
            'product_id': variant.id,
            'product_qty': self.quantity,
        })
        line.onchange_product_id()
        if purchase.account_analytic_id:
            line.account_analytic_id = purchase.account_analytic_id.id
        if purchase.date_planned:
            line.date_planned = purchase.date_planned
        return line

    @api.multi
    def fast_entry(self):
        """ Create one purchase order line per variant of a product template
        """
        self.ensure_one()
        purchase_ids = self.env.context.get('active_ids', [])
        purchase_model = self.env['purchase.order']
        purchases = purchase_model.browse(purchase_ids)
        lines = self.env['purchase.order.line'].browse()
        for purchase in purchases:
            for variant in self.product_tmpl_id.product_variant_ids:
                line = self._prepare_line(purchase, variant)
                lines |= line
            purchase.write({
                'order_line': [(0, 0, l._convert_to_write(l._cache))
                               for l in lines],
            })
        return {'type': 'ir.actions.act_window_close'}
