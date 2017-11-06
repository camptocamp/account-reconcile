# -*- coding: utf-8 -*-
# © 2014-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, api, _
from openerp.exceptions import ValidationError


class StockChangeProductQty(models.TransientModel):
    _inherit = "stock.change.product.qty"

    # When a user updates stock qty on the product form, propose the
    # right location to update stock.
    @api.model
    def default_get(self, fields):
        res = super(StockChangeProductQty, self).default_get(fields)
        active_id = self.env.context.get('active_id')
        if self.env.context.get('active_model') == 'product.template':
            product_ids = self.env['product.product'].search(
                [('product_tmpl_id', '=', active_id)]
            )
            if not product_ids:
                raise ValidationError(
                    _('The template "{}" has no active variant').format(
                        self.env['product.template'].browse(active_id).name
                    )
                )
        return res
