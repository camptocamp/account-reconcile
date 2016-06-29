# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..unit.binder import QoQaInheritsBinder
from ..backend import qoqa


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    qoqa_bind_service_ids = fields.One2many(
        comodel_name='qoqa.shipper.service',
        inverse_name='openerp_id',
        string='QoQa Bindings (Services)',
    )
    qoqa_bind_rate_ids = fields.One2many(
        comodel_name='qoqa.shipper.rate',
        inverse_name='openerp_id',
        string='QoQa Bindings (Rates)',
    )


class QoqaShipperRate(models.Model):
    """ QoQa Shipper Rate

    A shipper rate on QoQa is assigned to a deal and gives
    the shipping amount of the sales orders.

    """
    _name = 'qoqa.shipper.rate'
    _inherit = 'qoqa.binding'
    _inherits = {'delivery.carrier': 'openerp_id'}
    _description = 'QoQa Shipper Rate'

    openerp_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Delivery Method',
        required=True,
        index=True,
        ondelete='restrict',
    )


class QoqaShipperService(models.Model):
    """ QoQa Shipper Service

    A shipper service on QoQa represents the delivery method.
    It is the method used to print the shipping labels.

    """
    _name = 'qoqa.shipper.service'
    _inherit = 'qoqa.binding'
    _inherits = {'delivery.carrier': 'openerp_id'}
    _description = 'QoQa Shipper Service'

    openerp_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Delivery Method',
        required=True,
        index=True,
        ondelete='restrict',
    )


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
