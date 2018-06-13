# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _check_status_invoices(self):
        """Check statuses of invoices.

        At least one invoice should exist
        At least one invoice is paid
        All invoices are either paid or cancelled"""
        self.ensure_one()
        return (self.invoice_ids and
                u"paid" in self.invoice_ids.mapped("state") and
                all([rec.state in ("paid", "cancelled") for
                     rec in self.invoice_ids]))

    def _check_status_pickings(self):
        """Check statuses of pickings.

        At least one picking should exist
        At least one picking is done
        All pickings are either done or cancelled"""
        self.ensure_one()
        return (self.picking_ids and
                u"done" in self.picking_ids.mapped("state") and
                all([rec.state in ("done", "cancelled") for
                     rec in self.picking_ids]))

    def _check_billed(self):
        self.ensure_one()
        billed_lines = self.order_line.filtered(
            lambda x: x.product_qty == x.qty_invoiced
        )
        return bool(billed_lines)

    def _check_received(self):
        self.ensure_one()
        received_lines = self.order_line.filtered(
            lambda x: x.product_qty == x.qty_received
        )
        return bool(received_lines)

    def _check_statuses(self):
        """Check that pickings and invoices are in proper states.
        """
        self.ensure_one()
        pickings = self._check_status_pickings()
        invoices = self._check_status_invoices()
        billed = self._check_billed()
        recieved = self._check_received()
        return all((pickings, invoices, billed, recieved))

    @api.multi
    def mass_set_done_status(self):
        purchase_orders = self.search([('state', '=', 'purchase')]).filtered(
            lambda x: x._check_statuses() is True
        )
        purchase_orders.button_done()
