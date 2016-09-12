# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, exceptions, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # used in custom attributes
    brand = fields.Char(string='Brand',
                        related='product_brand_id.name',
                        readonly=True)

    @api.multi
    def run_orderpoint(self):
        variants = self.mapped('product_variant_ids')
        purchases = variants._run_orderpoint()
        return variants.action_open_generated_purchases(purchases.ids)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _run_orderpoint(self):
        orderpoints = self.mapped('orderpoint_ids')
        if not orderpoints:
            raise exceptions.UserError(
                _('The products have no orderpoints configured.')
            )

        procurement_ids = orderpoints.procure_orderpoint_confirm()
        procurements = self.env['procurement.order'].browse(procurement_ids)
        purchases = procurements.mapped('purchase_id')
        return purchases

    def run_orderpoint(self):
        purchases = self._run_orderpoint()
        return self.action_open_generated_purchases(purchases.ids)

    @api.multi
    def action_open_generated_purchases(self, purchase_ids):
        return {
            'domain': "[('id', 'in', %s)]" % purchase_ids,
            'name': _('Generated Purchases'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
