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


class qoqa_address(orm.Model):
    _name = 'qoqa.address'
    _inherit = 'qoqa.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _description = 'QoQa Address'

    _columns = {
        'openerp_id': fields.many2one('res.partner',
                                      string='Address',
                                      required=True,
                                      select=True,
                                      ondelete='restrict'),
        'created_at': fields.datetime('Created At (on QoQa)'),
        'updated_at': fields.datetime('Updated At (on QoQa)'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "An address with the same ID on QoQa already exists")
    ]


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'qoqa_address_bind_ids': fields.one2many(
            'qoqa.address',
            'openerp_id',
            string='QBindings for Addresses'),
        'digicode': fields.char('Digicode'),
        'qoqa_address': fields.boolean('Address from QoQa'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default['qoqa_address_bind_ids'] = False
        return super(res_partner, self).copy_data(cr, uid, id,
                                                  default=default,
                                                  context=context)


@qoqa
class AddressAdapter(QoQaAdapter):
    _model_name = 'qoqa.address'
    _endpoint = 'address'
