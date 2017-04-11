# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class StockMoveOperationLink(models.Model):
    _inherit = 'stock.move.operation.link'

    move_id = fields.Many2one(index=True)
    operation_id = fields.Many2one(index=True)
