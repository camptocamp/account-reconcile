# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    picking_id = fields.Many2one(index=True)
    product_id = fields.Many2one(index=True)
