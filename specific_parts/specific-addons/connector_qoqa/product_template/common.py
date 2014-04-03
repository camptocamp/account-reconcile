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


class qoqa_product_template(orm.Model):
    _name = 'qoqa.product.template'
    _inherit = 'qoqa.binding'
    _inherits = {'product.template': 'openerp_id'}
    _description = 'QoQa Template'

    _columns = {
        'openerp_id': fields.many2one('product.template',
                                      string='Template',
                                      required=True,
                                      select=True,
                                      ondelete='restrict'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A product with the same ID on QoQa already exists")
    ]


class product_template(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.product.template',
            'openerp_id',
            string='QoQa Bindings'),
        # deprecated (do not use the `deprecated` argument, it spams
        # warnings at each browse of a product
        'description_ecommerce': fields.html('E-commerce Description',
                                             translate=True),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(product_template, self).copy_data(
            cr, uid, id, default=default, context=context)


@qoqa
class QoQaTemplateAdapter(QoQaAdapter):
    _model_name = 'qoqa.product.template'
    _endpoint = 'product'
