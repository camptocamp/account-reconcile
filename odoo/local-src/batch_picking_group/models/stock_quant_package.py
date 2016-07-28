# -*- coding: utf-8 -*-
# © 2016 Cyril Gaudin (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class StockPackage(models.Model):
    _inherit = 'stock.quant.package'

    pack_operation_ids = fields.One2many(
        comodel_name='stock.pack.operation',
        inverse_name='result_package_id'
    )
