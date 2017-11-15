# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from operator import attrgetter
from itertools import groupby
from openerp import models
from openerp.addons.stock_batch_picking.report.batch_report import PrintBatch


class PrintBatchPacks(PrintBatch):

    def __init__(self, cr, uid, name, context):
        super(PrintBatchPacks, self).__init__(
            cr, uid, name, context=context
        )
        self.localcontext.update({
            'get_packs': self._get_packs,
            'get_variants': self._get_variants,
        })

    def _get_packs(self, batch_aggr):
        operations = sorted(
            batch_aggr.batch_id.pack_operation_ids,
            key=attrgetter('result_package_id.parcel_tracking')
        )
        for pack, operations in groupby(
                operations, key=attrgetter('result_package_id')
        ):
            yield pack, list(operations)

    def _get_variants(self, product):
        return ','.join(
            product.attribute_value_ids.mapped('name')
        )


class ReportPrintBatchPicking(models.AbstractModel):
    _inherit = 'report.stock_batch_picking.report_batch_picking'
    _wrapped_report_class = PrintBatchPacks
