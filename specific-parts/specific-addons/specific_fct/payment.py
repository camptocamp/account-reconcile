# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2013 Camptocamp SA
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
from openerp.osv import orm, fields
from openerp.addons.account_payment.wizard.account_payment_populate_statement \
    import account_payment_populate_statement as old_payment_wizard


class payment_order_create(orm.TransientModel):
    """
    Change default value to comment in order to send people the email
    (for claims)
    """
    _inherit = 'payment.order.create'

    def create_payment(self, cr, uid, ids, context=None):
        order_obj = self.pool.get('payment.order')
        line_obj = self.pool.get('account.move.line')
        payment_obj = self.pool.get('payment.line')
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        line_ids = [entry.id for entry in data.entries]
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        payment = order_obj.browse(cr, uid, context['active_id'],
                                   context=context)
        line2bank = line_obj.line2bank(cr, uid, line_ids, None, context)

        # Finally populate the current payment with new lines:
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            if payment.date_prefered == "now":
                # no payment date => immediate payment
                date_to_pay = False
            elif payment.date_prefered == 'due':
                date_to_pay = line.date_maturity
            elif payment.date_prefered == 'fixed':
                date_to_pay = payment.date_scheduled
            state = 'normal'
            if line.invoice and line.invoice.reference_type != 'none':
                state = 'structured'
            currency_id = line.invoice.currency_id.id if line.invoice else None
            if not currency_id:
                currency_id = line.journal_id.currency.id
            if not currency_id:
                currency_id = line.journal_id.company_id.currency_id.id
            payment_obj.create(
                cr, uid, {
                    'move_line_id': line.id,
                    'amount_currency': line.amount_residual_currency,
                    'bank_id': line2bank.get(line.id),
                    'order_id': payment.id,
                    'partner_id': line.partner_id.id,
                    'communication': line.ref or '/',
                    'state': state,
                    'date': date_to_pay,
                    'currency': currency_id,
                }, context=context)
        return {'type': 'ir.actions.act_window_close'}


# Temporary, until https://github.com/odoo/odoo/pull/9654 is merged
class PaymentLine(orm.Model):
    _inherit = 'payment.line'

    def _get_payment_move_line(self, cr, uid, ids, context=None):
        payment_line_obj = self.pool.get('payment.line')
        return payment_line_obj.search(cr, uid,
                                       [('move_line_id', 'in', ids)],
                                       context=context)

    def _get_move_line_values(self, cr, uid, ids, fields, arg, context=None):
        res = {}
        for payment_line in self.browse(cr, uid, ids):
            res[payment_line.id] = {'ml_date_created': False,
                                    'ml_maturity_date': False,
                                    'ml_inv_ref': False,
                                    'ml_reconcile_id': False,
                                    'ml_state': False}
            if payment_line.move_line_id:
                move_line = payment_line.move_line_id
                res[payment_line.id] = {
                    'ml_date_created': move_line.date_created,
                    'ml_maturity_date': move_line.date_maturity,
                    'ml_inv_ref': move_line.invoice and
                    move_line.invoice.id or False,
                    'ml_reconcile_id': move_line.reconcile_id and
                    move_line.reconcile_id.id or False,
                    'ml_state': move_line.state,
                }
        return res

    _move_line_store_condition = {
        'payment.line': (lambda self, cr, uid, ids, c=None: ids,
                         ['move_line_id'],
                         10),
        'account.move.line': (_get_payment_move_line,
                              ['date_created', 'date_maturity', 'invoice',
                               'reconcile_id', 'state'],
                              10),
    }

    _columns = {
        'ml_date_created': fields.function(
            _get_move_line_values, string="Effective Date", type='date',
            help="Invoice Effective Date",
            multi="move_line_values", store=_move_line_store_condition
        ),
        'ml_maturity_date': fields.function(
            _get_move_line_values, type='date', string='Due Date',
            multi="move_line_values", store=_move_line_store_condition
        ),
        'ml_inv_ref': fields.function(
            _get_move_line_values, type='many2one',
            relation='account.invoice', string='Invoice Ref.',
            multi="move_line_values", store=_move_line_store_condition
        ),
        'ml_reconcile_id': fields.function(
            _get_move_line_values, type='many2one',
            relation='account.move.reconcile', string='Move Line Reconcile',
            multi="move_line_values", store=_move_line_store_condition
        ),
        'ml_state': fields.function(
            _get_move_line_values, type='selection',
            selection=[('draft', 'Unbalanced'), ('valid', 'Balanced')],
            string='Move Line State',
            multi="move_line_values", store=_move_line_store_condition
        ),
    }


class AccountPaymentPopulateStatement(orm.TransientModel):
    _inherit = "account.payment.populate.statement"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        return super(old_payment_wizard, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=False)
