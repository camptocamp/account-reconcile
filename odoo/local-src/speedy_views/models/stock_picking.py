# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models
from .utils import create_index


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    claim_id = fields.Many2one(index=True)
    partner_id = fields.Many2one(index=True)
    batch_picking_id = fields.Many2one(index=True)
    group_id = fields.Many2one(index=True)

    def init(self, cr):

        # index for the default _order of stock.picking
        index_name = 'stock_picking_order_list_sort_desc_index'
        create_index(cr, index_name, self._table,
                     '(priority desc, date, id desc)')

        # this index is not created when we use
        # 'group_id = fields.Many2one(index=True')
        # so create it "manually"
        index_name = 'stock_picking_group_id_index'
        create_index(cr, index_name, self._table, '(group_id)')

        # active is mostly used with 'true' so this partial index improves
        # globally the queries. The same index on (active) without where
        # would in general not be used.
        index_name = 'stock_picking_active_true_index'
        create_index(cr, index_name, self._table, '(active) where active')
