# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _generate_swiss_pp_label(self, packing_ids=None):
        """ Generate labels and write tracking numbers received """
        self.ensure_one()
        report_name = 'delivery_carrier_label_swiss_pp.report_label_swiss_pp'

        pdf = self.env['report'].get_pdf(self, report_name)

        return {'name': '%s.pdf' % report_name,
                'file': pdf,
                'file_type': 'pdf',
                'package_id': packing_ids and packing_ids[0],
                }

    @api.multi
    def generate_shipping_labels(self, packing_ids=None):
        """ Add label generation for Swiss Post PP Franking"""
        self.ensure_one()
        if self.carrier_id.type == 'swiss_apost':
            return [self._generate_swiss_pp_label(packing_ids=packing_ids)]
        return super(StockPicking, self
                     ).generate_shipping_labels(packing_ids=packing_ids)
