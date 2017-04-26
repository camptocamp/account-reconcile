# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

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

        # this index is not created when we use
        # 'group_id = fields.Many2one(index=True')
        # so create it "manually"
        index_name = 'stock_picking_group_id_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                   (index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX %s ON stock_picking '
                       '(group_id) ' % index_name)

        # active is mostly used with 'true' so this partial index improves
        # globally the queries. The same index on (active) without where
        # would in general not be used.
        index_name = 'stock_picking_active_true_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                   (index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX %s ON stock_picking '
                       '(active) where active ' % index_name)
