# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp import _, api, models, fields
from openerp.exceptions import UserError

_logger = logging.getLogger(__name__)
try:
    from openerp.addons.connector.queue.job import job
    from openerp.addons.connector.session import ConnectorSession
except ImportError:
    _logger.debug('Can not `import connector`.')


class OfferUpdateWizard(models.TransientModel):
    _name = 'qoqa.offer.update.wizard'

    offer_ids = fields.Many2many(
        relation='qoqa_offer_update_ids_rel',
        comodel_name='qoqa.offer',
        string='Offers',
        required=True
    )

    @api.model
    def default_get(self, fields):
        res = super(OfferUpdateWizard, self).default_get(fields)
        if (self.env.context.get('active_model') == 'qoqa.offer' and
                self.env.context.get('active_ids')):
            offer_ids = self.env.context.get('active_ids')
            res['offer_ids'] = offer_ids
        return res

    @api.multi
    def _create_vat_jobs(self):
        account_invoice_obj = self.env['account.invoice']
        offer_ids = [x.id for x in self.offer_ids]
        all_invoices = account_invoice_obj.search(
            [('offer_id', 'in', offer_ids),
             ('state', '!=', 'cancel')])
        session = ConnectorSession.from_env(self.env)

        _logger.info(
            u'%s jobs for recompute TAX have been created.', (
                len(all_invoices)
            )
        )

        for invoice in all_invoices:
            recompute_one_invoice_tax.delay(session,
                                            'account.invoice', invoice.id)

    @api.multi
    def update_vat(self):
        if not self.offer_ids:
            raise UserError(_('Please Select at least one Offer'))
        self._create_vat_jobs()

    @api.multi
    def update_account(self):
        if not self.offer_ids:
            raise UserError(_('Please Select at least one Offer'))
        self._create_account_jobs()

    @api.multi
    def _create_account_jobs(self):
        account_invoice_obj = self.env['account.invoice']
        offer_ids = [x.id for x in self.offer_ids]
        all_invoices = account_invoice_obj.search(
            [('offer_id', 'in', offer_ids),
             ('state', '!=', 'cancel')])
        session = ConnectorSession.from_env(self.env)

        # maybe not creating too many dictionaries will make us a bit faster
        _logger.info(
            u'%s jobs for recompute TAX have been created.', len(all_invoices)
            )

        for invoice in all_invoices:
            recompute_one_invoice_account.delay(session,
                                                'account.invoice', invoice.id,
                                                )


@job(default_channel='root.qoqa_offer_update')
def recompute_one_invoice_tax(session, model_name, invoice_id):
    """Reassign correct tax on invoice"""
    InvoiceLine = session.env['account.invoice.line']
    invoice = session.env[model_name].browse(invoice_id)
    if invoice.exists():
        unreconcile_from_invoice(invoice)
        invoice_lines = InvoiceLine.search(
            [('invoice_id', '=', invoice_id)])
        for invoice_line in invoice_lines:
            if invoice_line.product_id.taxes_id != \
                    invoice_line.invoice_line_tax_ids:
                _logger.info("REWRITE TAXES for invoice %s", invoice.name)
                tax_tab = [x.id for x in invoice_line.product_id.taxes_id]
                invoice_line.sale_line_ids.write(
                    {'tax_id': [(6, 0, tax_tab)]})
                invoice_line.write(
                    {'invoice_line_tax_ids': [(6, 0, tax_tab)]}
                )
                _logger.info("REWRITE TAXES for invoice %s done", invoice.name)
        invoice.signal_workflow('invoice_open')


@job(default_channel='root.qoqa_offer_update')
def recompute_one_invoice_account(session, model_name, invoice_id):
    """Reassign correct account on invoice"""
    InvoiceLine = session.env['account.invoice.line']
    invoice = session.env[model_name].browse(invoice_id)
    if invoice.exists():
        unreconcile_from_invoice(invoice)
        invoice_lines = InvoiceLine.search(
            [('invoice_id', '=', invoice_id)])
        for invoice_line in invoice_lines:
            inv_prd = invoice_line.product_id
            account = inv_prd.property_account_income_id or \
                inv_prd.categ_id.property_account_income_categ_id
            if invoice_line.account_id.id != account.id:
                _logger.info("REWRITE ACCOUNT for invoice %s", invoice.name)
                invoice_line.write(
                    {'account_id': account.id})
                _logger.info("REWRITE ACCOUNT for invoice %s done",
                             invoice.name)
    invoice.signal_workflow('invoice_open')


@api.multi
def unreconcile_from_invoice(invoice):
    if invoice.move_id:
        _logger.info(
            u"try to unreconcile invoice {}".format(invoice.number))
        move = invoice.move_id
        for move_line in move.line_ids:
            move_line.remove_move_reconcile()
        invoice.action_cancel()
        invoice.action_cancel_draft()
