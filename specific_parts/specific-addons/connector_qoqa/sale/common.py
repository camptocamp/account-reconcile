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
        'total_amount': fields.float(
            'Total amount',
            digits_compute=dp.get_precision('Account')),
        'invoice_ref': fields.char('Invoice Ref. on QoQa'),
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
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(sale_order, self).copy_data(cr, uid, id,
                                                 default=default,
                                                 context=context)


@qoqa
class QoQaSaleOrder(QoQaAdapter):
    _model_name = 'qoqa.sale.order'
    _endpoint = 'order'
