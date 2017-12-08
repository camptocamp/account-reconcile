# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from itertools import groupby
from openerp import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    first_package_name = fields.Char(
        compute='_compute_first_package_name',
        string='First Package Name',
    )

    @api.depends('pack_operation_ids.result_package_id.name')
    def _compute_first_package_name(self):
        for record in self:
            record.first_package_name = record.mapped(
                'pack_operation_ids.result_package_id.name'
            )[0]

    @api.multi
    def _generate_swiss_pp_label(self, package_ids=None):
        """ Generate labels and write tracking numbers received """
        self.ensure_one()
        report_name = 'delivery_carrier_label_swiss_pp.report_label_swiss_pp'
        pdf = self.env['report'].get_pdf(self, report_name)

        return {'name': '%s.pdf' % report_name,
                'file': pdf,
                'file_type': 'pdf',
                'package_id': package_ids and package_ids[0],
                }

    @api.multi
    def generate_shipping_labels(self, package_ids=None):
        """ Add label generation for Swiss Post PP Franking"""
        self.ensure_one()
        if self.carrier_id.carrier_type == 'swiss_apost':
            return [self._generate_swiss_pp_label(package_ids=package_ids)]
        return super(StockPicking, self
                     ).generate_shipping_labels(package_ids=package_ids)


class DeliveryCarrierLabelGenerate(models.TransientModel):

    _inherit = 'delivery.carrier.label.generate'

    @api.model
    def _get_packs(self, batch):
        """Override to change sort order for QoQa"""
        # reload ?
        batch = self.env['stock.batch.picking'].browse(batch.id)

        def _sort_key(rec):
            return (rec.result_package_id.parcel_tracking or
                    rec.result_package_id.name or
                    rec.package_id.name)
        operations = batch.pack_operation_ids
        operations = sorted(
            operations,
            key=_sort_key
        )

        packs = []
        for pack, grp_operations in groupby(
                operations,
                key=lambda r: r.result_package_id or r.package_id):
            pack_label = self._find_pack_label(pack)
            packs.append((pack, list(grp_operations), pack_label))
        return packs