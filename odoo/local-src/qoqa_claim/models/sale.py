# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _last_invoice(self):
        self.ensure_one()
        invoices = self.invoice_ids.filtered(
            lambda invoice: invoice.state != 'cancel'
        )
        invoices = invoices.sorted(key=lambda i: i.date_invoice, reverse=True)
        if len(invoices) > 1:
            return invoices[0]
        return invoices
