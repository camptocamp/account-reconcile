# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, api, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    claim_id = fields.Many2one(index=True)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    sale_line_id = fields.Many2one(index=True)

    @api.model
    def create(self, vals):
        self_no_track = self.with_context(tracking_disable=True)
        return super(ProcurementOrder, self_no_track).create(vals)

    @api.multi
    def write(self, vals):
        self_no_track = self.with_context(tracking_disable=True)
        return super(ProcurementOrder, self_no_track).write(vals)
