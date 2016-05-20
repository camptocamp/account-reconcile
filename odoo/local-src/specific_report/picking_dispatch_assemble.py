# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import pooler
from openerp.addons.base_report_assembler import report_assembler


class PickingDispatchPDFReportAssembler(report_assembler.PDFReportAssembler):
    """InvoicePDFReportAssembler allows to merge multiple
    invoice reports into one pdf"""

    def _get_report_ids(self, cr, uid, ids, context=None):
        pool = pooler.get_pool(cr.dbname)
        assemble_obj = pool['assembled.report']
        report_ids = assemble_obj.search(cr, uid,
                                         [('model', '=', 'picking.dispatch')],
                                         order="sequence",
                                         context=context)
        reports = assemble_obj.browse(cr, uid, report_ids, context=context)
        return [r.report_id.id for r in reports]

PickingDispatchPDFReportAssembler('report.picking_dispatch_report_assemblage',
                                  'picking.dispatch',
                                  None)
