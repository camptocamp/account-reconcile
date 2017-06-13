# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models
from .utils import create_index


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    picking_id = fields.Many2one(index=True)
    product_id = fields.Many2one(index=True)

    def init(self, cr):
        # index for result_package and product (from Odoo SA)
        index_name = 'stock_pack_operation_package_product_index'
        create_index(cr, index_name,
                     self._table, '(result_package_id, product_id)')
