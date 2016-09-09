# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models


class ProductOrderpointConfirm(models.TransientModel):
    _name = 'product.orderpoint.confirm'
    _description = 'Product Orderpoint Confirm'

    @api.multi
    def action_confirm(self):
        self.ensure_one()

        product_ids = self.env.context.get('active_ids')
        assert product_ids and isinstance(product_ids, list)
        model = self.env.context.get('active_model')
        return self.env[model].browse(product_ids).run_orderpoint()
