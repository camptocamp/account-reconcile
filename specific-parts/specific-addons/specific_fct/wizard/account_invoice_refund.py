# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class account_invoice_refund(orm.TransientModel):
    _inherit = 'account.invoice.refund'

    def _get_warning_message(self, cr, uid, context=None):
        active_id = context and context.get('active_id', False)
        if active_id:
            inv = self.pool.get('account.invoice').browse(cr, uid, active_id,
                                                          context=context)
            inv_date = datetime.strptime(inv.date_invoice,
                                         DEFAULT_SERVER_DATE_FORMAT)
            delta = datetime.now() - inv_date
            delta_days = delta.days
            payments = inv.sale_ids
            for payment in payments:
                if (payment.payment_method_id.refund_min_date and
                        payment.payment_method_id.refund_min_date >
                        inv.date_invoice):
                    return ("La commande ne sera pas remboursée par le "
                            "provider de paiement (Datatrans, Mercanet, "
                            "etc.) car il s'agit d'une commande "
                            "datantrans d'avant le " +
                            payment.payment_method_id.refund_min_date)
                elif (payment.payment_method_id.refund_max_days and
                      payment.payment_method_id.refund_max_days <
                      delta_days):
                    return ("La commande ne sera pas remboursée par le "
                            "provider de paiement (Datatrans, Mercanet, "
                            "etc.) car la méthode de paiement n'autorise "
                            "le remboursement que pour %s jours maximum"
                            % (payment.payment_method_id.refund_max_days))
            if len(inv.refund_ids) > 0:
                return ("La commande possède déjà %i avoir(s)" %
                        len(inv.refund_ids))
            return ''

    _columns = {
        'warning': fields.char('Warning'),
    }

    _defaults = {
        'warning': _get_warning_message,
    }
