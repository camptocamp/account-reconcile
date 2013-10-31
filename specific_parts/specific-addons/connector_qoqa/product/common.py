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

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class qoqa_product_product(orm.Model):
    _name = 'qoqa.product.product'
    _inherit = 'qoqa.binding'
    _inherits = {'product.product': 'openerp_id'}
    _description = 'QoQa Product'

    _columns = {
        'openerp_id': fields.many2one('product.product',
                                      string='Product',
                                      required=True,
                                      ondelete='restrict'),
        'created_at': fields.date('Created At (on QoQa)'),
        'updated_at': fields.date('Updated At (on QoQa)'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A product with the same ID on QoQa already exists")
    ]


class product_product(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.product.product',
            'openerp_id',
            string='QoQa Bindings'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(product_product, self).copy_data(cr, uid, id,
                                                      default=default,
                                                      context=context)
@qoqa
class QoQaProductAdapter(QoQaAdapter):
    _model_name = 'qoqa.product.product'
    _endpoint = 'variation'
