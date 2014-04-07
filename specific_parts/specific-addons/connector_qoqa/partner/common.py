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
from ..unit.binder import QoQaBinder
from ..backend import qoqa


class qoqa_res_partner(orm.Model):
    _name = 'qoqa.res.partner'
    _inherit = 'qoqa.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _description = 'QoQa User'

    _columns = {
        'openerp_id': fields.many2one('res.partner',
                                      string='Customer',
                                      required=True,
                                      select=True,
                                      ondelete='restrict'),
        'qoqa_name': fields.char('QoQa Name'),
        'qoqa_active': fields.boolean('QoQa Active'),
        'suspicious': fields.boolean('Suspicious'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
        'origin_shop_id': fields.many2one('qoqa.shop',
                                          'Origin Shop'),
        'qoqa_status': fields.selection(
            [('prospect', 'Prospect'),
             ('active', 'Active')],
            string='Status on QoQa',
            readonly=True),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "An user with the same ID on QoQa already exists"),
    ]


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'qoqa_bind_ids': fields.one2many(
            'qoqa.res.partner',
            'openerp_id',
            string='QBindings'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_bind_ids'] = False
        return super(res_partner, self).copy_data(cr, uid, id,
                                                  default=default,
                                                  context=context)


@qoqa
class ResPartnerAdapter(QoQaAdapter):
    _model_name = 'qoqa.res.partner'
    _endpoint = 'user'


@qoqa
class CustomerStatusBinder(QoQaBinder):
    """ 'Fake' binder: hard code bindings

    ``qoqa_status`` is a selection field on
    `qoqa.res.partner``.

    The binding is a mapping between the name of the
    selection on OpenERP and the id on QoQa.

    """
    _model_name = 'qoqa.customer.status'

    qoqa_bindings = {1: 'prospect', 2: 'active'}
    # inverse mapping
    openerp_bindings = dict((v, k) for k, v in qoqa_bindings.iteritems())

    def to_openerp(self, external_id, unwrap=False):
        return self.qoqa_bindings[external_id]

    def to_backend(self, binding_id, wrap=False):
        return self.openerp_bindings[binding_id]

    def bind(self, external_id, binding_id):
        raise TypeError('%s cannot be synchronized' % self._model_name)
