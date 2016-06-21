# -*- coding: utf-8 -*-
# © 2004-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    def _get_warning_message(self):
        invoice_model = self.env['account.invoice']

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

        payments = invoice.sale_ids
        for payment in payments:
            if (payment.payment_method_id.refund_min_date and
                    payment.payment_method_id.refund_min_date >
                    invoice.date_invoice):
                return (
                    "La commande ne sera pas remboursée par le "
                    "provider de paiement (Datatrans, Mercanet, "
                    "etc.) car il s'agit d'une commande "
                    "datantrans d'avant le " +
                    payment.payment_method_id.refund_min_date
                )
            elif (payment.payment_method_id.refund_max_days and
                  payment.payment_method_id.refund_max_days <
                  delta_days):
                return (
                    "La commande ne sera pas remboursée par le "
                    "provider de paiement (Datatrans, Mercanet, "
                    "etc.) car la méthode de paiement n'autorise "
                    "le remboursement que pour %s jours maximum"
                    % payment.payment_method_id.refund_max_days
                )
        if len(invoice.refund_ids) > 0:
            return ("La commande possède déjà %d avoir(s)" %
                    len(invoice.refund_ids))
        return ''

    warning = fields.Char('Warning', default=_get_warning_message)
