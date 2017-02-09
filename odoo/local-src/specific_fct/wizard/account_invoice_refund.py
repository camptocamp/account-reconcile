# -*- coding: utf-8 -*-
# © 2004-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import UserError
from datetime import datetime


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    def _get_warning_message(self):
        invoice_model = self.env['account.invoice']
        sale_order_model = self.env['sale.order']

        invoice = False
        # Check that we called the wizard from an invoice
        if self.env.context.get('active_model', False) == 'account.invoice':
            active_id = self.env.context.get('active_id', False)
        else:
            active_id = False

        if active_id:
            invoice = invoice_model.browse(active_id)
        else:
            # For RMAs, the ID is in context['invoice_ids']
            invoice_ids = self.env.context.get('invoice_ids')
            if invoice_ids:
                invoice = invoice_model.browse(invoice_ids[0])

        if not (invoice and invoice.date_invoice):
            return ("La facture ne possède pas de date de facturation! "
                    "Veuillez ajouter une date de facturation avant de "
                    "continuer.")
        inv_date = datetime.strptime(invoice.date_invoice,
                                     DEFAULT_SERVER_DATE_FORMAT)
        delta_days = (datetime.now() - inv_date).days

        sales = sale_order_model.search([('name', '=', invoice.origin)])
        for sale in sales:
            if (sale.payment_mode_id.refund_min_date and
                    sale.payment_mode_id.refund_min_date >
                    invoice.date_invoice):
                return (
                    "La commande ne sera pas remboursée par le "
                    "provider de paiement (Datatrans, Mercanet, "
                    "etc.) car il s'agit d'une commande "
                    "datantrans d'avant le " +
                    sale.payment_mode_id.refund_min_date
                )
            elif (sale.payment_mode_id.refund_max_days and
                  sale.payment_mode_id.refund_max_days <
                  delta_days):
                return (
                    "La commande ne sera pas remboursée par le "
                    "provider de paiement (Datatrans, Mercanet, "
                    "etc.) car la méthode de paiement n'autorise "
                    "le remboursement que pour %s jours maximum"
                    % sale.payment_mode_id.refund_max_days
                )
        if len(invoice.refund_ids) > 0:
            return ("La commande possède déjà %d avoir(s)" %
                    len(invoice.refund_ids))
        return ''

    @api.multi
    def compute_refund(self, mode='refund'):
        inv_obj = self.env['account.invoice']
        inv_tax_obj = self.env['account.invoice.tax']
        inv_line_obj = self.env['account.invoice.line']
        context = dict(self._context or {})
        xml_id = False

        for form in self:
            created_inv = []
            for inv in inv_obj.browse(context.get('active_ids')):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise UserError(
                        _('Cannot refund draft/proforma/cancelled invoice.'))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise UserError(
                        _('Cannot refund invoice which is already '
                          'reconciled, invoice should be unreconciled first. '
                          'You can only refund this invoice.'))

                date = form.date or False
                description = form.description or inv.name
                if form.refund_description_id:
                    description = form.refund_description_id.name
                    description_id = form.refund_description_id.id
                refund = inv.refund_with_description_id(
                    form.date_invoice, date, description, inv.journal_id.id,
                    description_id)
                refund.compute_taxes()

                created_inv.append(refund.id)
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_ids
                    to_reconcile_ids = {}
                    to_reconcile_lines = self.env['account.move.line']
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_lines += line
                            to_reconcile_ids.setdefault(
                                line.account_id.id, []).append(line.id)
                        if line.reconciled:
                            line.remove_move_reconcile()
                    refund.signal_workflow('invoice_open')
                    for tmpline in refund.move_id.line_ids:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_lines += tmpline
                            to_reconcile_lines.reconcile()
                    if mode == 'modify':
                        invoice = inv.read(
                            ['name', 'type', 'number', 'reference',
                             'comment', 'date_due', 'partner_id',
                             'partner_insite', 'partner_contact',
                             'partner_ref', 'payment_term_id', 'account_id',
                             'currency_id', 'invoice_line_ids', 'tax_line_ids',
                             'journal_id', 'date'])
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.browse(
                            invoice['invoice_line_ids'])
                        invoice_lines = inv_obj.with_context(
                            mode='modify')._refund_cleanup_lines(invoice_lines)
                        tax_lines = inv_tax_obj.browse(invoice['tax_line_ids'])
                        tax_lines = inv_obj._refund_cleanup_lines(tax_lines)
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': form.date_invoice,
                            'state': 'draft',
                            'number': False,
                            'invoice_line_ids': invoice_lines,
                            'tax_line_ids': tax_lines,
                            'date': date,
                            'name': description,
                            'origin': inv.origin,
                            'fiscal_position_id': inv.fiscal_position_id.id,
                            'refund_description_id': description_id,
                        })
                        for field in ('partner_id', 'account_id',
                                      'currency_id', 'payment_term_id',
                                      'journal_id'):
                                invoice[field] = invoice[field] and \
                                    invoice[field][0]
                        inv_refund = inv_obj.create(invoice)
                        if inv_refund.payment_term_id.id:
                            inv_refund._onchange_payment_term_date_invoice()
                        created_inv.append(inv_refund.id)
                xml_id = ((inv.type in ['out_refund', 'out_invoice']) and
                          'action_invoice_tree1' or
                          (inv.type in ['in_refund', 'in_invoice']) and
                          'action_invoice_tree2')
                # Put the reason in the chatter
                subject = _("Invoice refund")
                body = description
                refund.message_post(body=body, subject=subject)
        if xml_id:
            result = self.env.ref('account.%s' % xml_id).read()[0]
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True

    warning = fields.Char('Warning', default=_get_warning_message)
    refund_description_id = fields.Many2one(
        'account.refund.description', 'Description', select=True)
