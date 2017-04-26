# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import models
from .utils import create_index


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def init(self, cr):
        # active is mostly used with 'true' so this partial index improves
        # globally the queries. The same index on (active) without where
        # would in general not be used.
        index_name = 'purchase_order_active_true_index'
        create_index(cr, index_name, self._table, '(active) where active')
