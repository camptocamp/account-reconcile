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


class qoqa_sale_order_line(orm.Model):
    _name = 'qoqa.sale.order.line'
    _inherit = 'qoqa.binding'
    _inherits = {'sale.order.line': 'openerp_id'}
    _description = 'QoQa Sales Order Line'

    _columns = {
        'openerp_id': fields.many2one('sale.order.line',
                                      string='Sales Order Line',
                                      required=True,
                                      select=True,
                                      ondelete='restrict'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
        'qoqa_order_id': fields.many2one('qoqa.sale.order',
                                         'QoQa Sale Order',
                                         required=True,
                                         readonly=True,
                                         ondelete='cascade',
                                         select=True),
        'qoqa_quantity': fields.integer('Quantity'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A sales order line with the same ID on QoQa already exists")
    ]

    def create(self, cr, uid, vals, context=None):
        qoqa_order_id = vals['qoqa_order_id']
        qsale_obj = self.pool['qoqa.sale.order']
        qsale = qsale_obj.read(cr, uid, qoqa_order_id,
                               ['openerp_id'], context=context)
        order_id = qsale['openerp_id']
        vals['order_id'] = order_id[0]
        res = super(qoqa_sale_order_line, self).create(
            cr, uid, vals, context=context)
        return res


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.sale.order.line',
            'openerp_id',
            string='QBindings'),
        'custom_text': fields.char('Custom Text'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(sale_order_line, self).copy_data(
            cr, uid, id, default=default, context=context)
