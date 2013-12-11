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

from ..unit.binder import QoQaInheritsBinder
from ..backend import qoqa


class delivery_carrier(orm.Model):
    _inherit = 'delivery.carrier'

    _columns = {
        'qoqa_bind_service_ids': fields.one2many(
            'qoqa.shipper.service', 'openerp_id',
            string='QoQa Bindings (Services)',
            readonly=True),
        'qoqa_bind_rate_ids': fields.one2many(
            'qoqa.shipper.rate', 'openerp_id',
            string='QoQa Bindings (Rates)',
            readonly=True),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_bind_service_ids': False,
            'qoqa_bind_rate_ids': False,
        })
        return super(delivery_carrier, self).copy_data(
            cr, uid, id, default=default, context=context)


class qoqa_shipper_rate(orm.Model):
    """ QoQa Shipper Rate

    A shipper rate on QoQa is assigned to a deal and gives
    the shipping amount of the sales orders.

    """
    _name = 'qoqa.shipper.rate'
    _inherit = 'qoqa.binding'
    _inherits = {'delivery.carrier': 'openerp_id'}
    _description = 'QoQa Shipper Rate'

    _columns = {
        'openerp_id': fields.many2one('delivery.carrier',
                                      string='Delivery Method',
                                      required=True,
                                      ondelete='restrict'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A shipper rate with the same ID on QoQa already exists")
    ]


class qoqa_shipper_service(orm.Model):
    """ QoQa Shipper Service

    A shipper service on QoQa represents the delivery method.
    It is the method used to print the shipping labels.

    """
    _name = 'qoqa.shipper.service'
    _inherit = 'qoqa.binding'
    _inherits = {'delivery.carrier': 'openerp_id'}
    _description = 'QoQa Shipper Service'

    _columns = {
        'openerp_id': fields.many2one('delivery.carrier',
                                      string='Delivery Method',
                                      required=True,
                                      ondelete='restrict'),
    }

    _sql_constraints = [
        ('qoqa_uniq', 'unique(backend_id, qoqa_id)',
         "A shipper rate with the same ID on QoQa already exists")
    ]


@qoqa
class ShipperBinder(QoQaInheritsBinder):
    _model_name = ['qoqa.shipper.service',
                   'qoqa.shipper.rate',
                   ]

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        raise TypeError('%s cannot be synchronized' % self.model._name)
