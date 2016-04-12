# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    offer_id = fields.Many2one(
        comodel_name='qoqa.offer',
        string='Offer',
        readonly=True,
        index=True,
        ondelete='restrict',
    )

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        result = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        if invoice.offer_id:
            result['offer_id'] = invoice.offer_id.id
        return result
