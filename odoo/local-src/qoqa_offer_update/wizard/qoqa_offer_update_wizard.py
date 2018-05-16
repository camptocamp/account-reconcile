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
        offer_ids = self.offer_ids.ids
        session = ConnectorSession.from_env(self.env)
        batch_recompute_invoice_tax.delay(
            session,
            'account.invoice',
            offer_ids,
            priority=40
        )

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
        offer_ids = self.offer_ids.ids
        session = ConnectorSession.from_env(self.env)
        batch_recompute_invoice_account.delay(
            session,
            'account.invoice',
            offer_ids,
            priority=40
        )


@job(default_channel='root.qoqa_offer_update')
def batch_recompute_invoice_tax(session, model_name, offer_ids):
    """Batch: create jobs for reassign correct tax on invoice"""
    account_invoice_obj = session.env['account.invoice']
    all_invoices = account_invoice_obj.search(
        [('offer_id', 'in', offer_ids),
         ('state', '!=', 'cancel')]
    )

    for invoice in all_invoices:
        recompute_one_invoice_tax.delay(session,
                                        'account.invoice', invoice.id,
                                        priority=40)

    message = (
        u'%s jobs for recompute TAX have been created.' %
        (len(all_invoices),)
    )
    _logger.info(message)
    return message


@job(default_channel='root.qoqa_offer_update')
def recompute_one_invoice_tax(session, model_name, invoice_id):
    """Reassign correct tax on invoice"""
    invoice = session.env[model_name].browse(invoice_id)
    if not invoice.exists():
        return
    invoice_lines = session.env['account.invoice.line'].search(
        [('invoice_id', '=', invoice_id)]
    )
    if all(l.product_id.taxes_id == l.invoice_line_tax_ids
           for l in invoice_lines):
        # we are already good for this invoice
        return _('taxes already correct')
    unreconcile_from_invoice(invoice)
    for invoice_line in invoice_lines:
        if invoice_line.product_id.taxes_id != \
                invoice_line.invoice_line_tax_ids:
            _logger.info("REWRITE TAXES for invoice %s", invoice.name)
            tax_ids = invoice_line.product_id.taxes_id.ids
            invoice_line.sale_line_ids.write(
                {'tax_id': [(6, 0, tax_ids)]})
            invoice_line.write(
                {'invoice_line_tax_ids': [(6, 0, tax_ids)]}
            )
            _logger.info("REWRITE TAXES for invoice %s done", invoice.name)
    invoice.compute_taxes()
    invoice.signal_workflow('invoice_open')


@job(default_channel='root.qoqa_offer_update')
def batch_recompute_invoice_account(session, model_name, offer_ids):
    """Batch: create jobs for reassign correct account on invoice"""
    account_invoice_obj = session.env['account.invoice']
    all_invoices = account_invoice_obj.search(
        [('offer_id', 'in', offer_ids),
         ('state', '!=', 'cancel')]
    )
    for invoice in all_invoices:
        recompute_one_invoice_account.delay(session,
                                            'account.invoice', invoice.id,
                                            priority=40
                                            )
    message = (
        u'%s jobs for recompute accounts have been created.' %
        (len(all_invoices),)
    )
    _logger.info(message)
    return message


@job(default_channel='root.qoqa_offer_update')
def recompute_one_invoice_account(session, model_name, invoice_id):
    """Reassign correct account on invoice"""
    invoice_lines = session.env['account.invoice.line'].search(
        [('invoice_id', '=', invoice_id)]
    )
    for invoice_line in invoice_lines:
        product = invoice_line.product_id
        if invoice_line.account_id.reconcile:
            # we can't change safely accounts on reconcilable accounts
            continue
        account = (
            product.property_account_income_id or
            product.categ_id.property_account_income_categ_id
        )
        if invoice_line.account_id == account:
            # already correct
            continue
        invoice_line.write({'account_id': account.id})

    move_lines = session.env['account.move.line'].search(
        [('invoice_id', '=', invoice_id)]
    )
    for move_line in move_lines:
        product = move_line.product_id
        if not product:
            continue
        if move_line.account_id.reconcile:
            # we can't change safely accounts on reconcilable accounts
            continue
        account = (
            product.property_account_income_id or
            product.categ_id.property_account_income_categ_id
        )
        if move_line.account_id == account:
            # already correct
            continue

        # we can change only the account, as this is the account of the product
        # we assume it's safe, we'll never reconcile this line
        session.env.cr.execute(
            'UPDATE account_move_line SET '
            'account_id = %s WHERE id = %s',
            (account.id, move_line.id)
        )


@api.multi
def unreconcile_from_invoice(invoice):
    if invoice.move_id:
        _logger.info(
            u"try to unreconcile invoice {}".format(invoice.number))
        move = invoice.move_id
        for move_line in move.line_ids:
            move_line.remove_move_reconcile()
        invoice.with_context(no_cancel_refund=True).action_cancel()
        invoice.action_cancel_draft()
