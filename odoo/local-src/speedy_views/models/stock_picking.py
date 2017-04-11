# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    group_id = fields.Many2one(index=True)
    claim_id = fields.Many2one(index=True)
    batch_picking_id = fields.Many2one(index=True)

    def init(self, cr):

        # index for the default _order of stock.picking
        index_name = 'stock_picking_order_list_sort_desc_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                   (index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX %s '
                       'ON stock_picking '
                       '(priority desc, date, id desc) ' % index_name)
