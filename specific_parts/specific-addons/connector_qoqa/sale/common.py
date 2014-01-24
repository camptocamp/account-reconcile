# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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

import json
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class qoqa_sale_order(orm.Model):
    _name = 'qoqa.sale.order'
    _inherit = 'qoqa.binding'
    _inherits = {'sale.order': 'openerp_id'}
    _description = 'QoQa User'

    _columns = {
        'openerp_id': fields.many2one('sale.order',
                                      string='Sales Order',
                                      required=True,
                                      ondelete='restrict'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
        'qoqa_shop_id': fields.many2one(
            'qoqa.shop',
            string='QoQa Shop',
            required=True,
            readonly=True),
        'qoqa_order_line_ids': fields.one2many('qoqa.sale.order.line',
                                               'qoqa_order_id',
                                               'QoQa Order Lines'),
        'qoqa_amount_total': fields.float(
            'Total amount on QoQa',
            digits_compute=dp.get_precision('Account')),
        'invoice_ref': fields.char('Invoice Ref. on QoQa'),
        # id of the main payment on qoqa, used as key for reconciliation
        'qoqa_payment_id': fields.char('ID of the payment on QoQa'),
        # field with name 'transaction' in the main payment
        'qoqa_transaction': fields.char('Transaction number of the payment '
                                        'on QoQa'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A sales order with the same ID on QoQa already exists")
    ]


class sale_order(orm.Model):
    _inherit = 'sale.order'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.sale.order',
            'openerp_id',
            string='QBindings'),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(sale_order, self).copy_data(cr, uid, id,
                                                 default=default,
                                                 context=context)

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        values = super(sale_order, self)._prepare_invoice(
            cr, uid, order, lines, context=context)
        if order.qoqa_bind_ids:
            binding = order.qoqa_bind_ids[0]
            # keep only the issued invoice from the qoqa backend
            values.update({
                'name': binding.invoice_ref,
                # restore order's name, don't want the concatenated
                # invoices numbers
                'reference': order.name,
            })
        return values


@qoqa
class QoQaSaleOrderAdapter(QoQaAdapter):
    _model_name = 'qoqa.sale.order'
    _endpoint = 'order'

    def cancel(self, id):
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        response = self.client.put(url + str(id),
                                   data=json.dumps({'action': 'cancel'}),
                                   headers=headers)
        self._handle_response(response)

    def refund(self, id, payment_id, amount):
        """ Create a refund on the QoQa backend, return the payment id """
        url = self.url(with_lang=False)
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        payload = {'action': 'credit',
                   'refno': payment_id,
                   'amount': amount}
        response = self.client.put(url + str(id),
                                   data=json.dumps(payload),
                                   headers=headers)
        response = self._handle_response(response)
        # TODO I do not know the content of the response actually
        # it should return the ID of the payment
        return response['id']
