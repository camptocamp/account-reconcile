# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..unit.binder import QoQaInheritsBinder
from ..backend import qoqa


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    qoqa_bind_package_type_ids = fields.One2many(
        comodel_name='qoqa.shipper.package.type',
        inverse_name='openerp_id',
        string='QoQa Bindings (Package Types)',
    )
    qoqa_bind_fee_ids = fields.One2many(
        comodel_name='qoqa.shipper.fee',
        inverse_name='openerp_id',
        string='QoQa Bindings (Rates)',
    )


class QoqaShipperPackageType(models.Model):
    """ QoQa Shipper Package Type

    This is want we send alongside to the tracking number
    to the QoQa API to show what the delivery method was.

    """
    _name = 'qoqa.shipper.package.type'
    _inherit = 'qoqa.binding'
    _inherits = {'delivery.carrier': 'openerp_id'}
    _description = 'QoQa Shipper Package Type'

    openerp_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Delivery Method',
        required=True,
        index=True,
        ondelete='restrict',
    )

    def _auto_init(self, cr, context=None):
        # remove the uniq constraint (from qoqa.binding), because
        # we should be allowed to have several delivery methods on Odoo
        # for one on QoQa
        self._sql_constraints = filter(
            lambda (name, __, ___): name != 'qoqa_binding_uniq',
            self._sql_constraints
        )
        super(QoqaShipperPackageType, self)._auto_init(cr, context=context)


class QoqaShipperFee(models.Model):
    """ QoQa Shipper Fee

    Used on QoQa for the amount of the shipping fee.
    We map it in order to set the name and the product_id of the shipping order
    line.

    """
    _name = 'qoqa.shipper.fee'
    _inherit = 'qoqa.binding'
    _inherits = {'delivery.carrier': 'openerp_id'}
    _description = 'QoQa Shipper Fee'

    openerp_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Delivery Method',
        required=True,
        index=True,
        ondelete='restrict',
    )


@qoqa
class ShipperBinder(QoQaInheritsBinder):
    _model_name = ['qoqa.shipper.package.type',
                   'qoqa.shipper.fee',
                   ]

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        raise TypeError('%s cannot be synchronized' % self.model._name)
