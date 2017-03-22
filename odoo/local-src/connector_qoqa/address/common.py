# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaAddress(models.Model):
    _name = 'qoqa.address'
    _inherit = 'qoqa.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _description = 'QoQa Address'

    openerp_id = fields.Many2one(comodel_name='res.partner',
                                 string='Address',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    created_at = fields.Datetime(string='Created At (on QoQa)')
    updated_at = fields.Datetime(string='Updated At (on QoQa)')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    qoqa_address_bind_ids = fields.One2many(
        'qoqa.address',
        'openerp_id',
        string='QBindings for Addresses',
        copy=False,
        context={'active_test': False},
    )
    digicode = fields.Char('Digicode')
    qoqa_address = fields.Boolean('Address from QoQa',
                                  default=False)
    qoqa_order_address = fields.Boolean('Address from a QoQa Sale',
                                        default=False)


@qoqa
class AddressAdapter(QoQaAdapter):
    _model_name = 'qoqa.address'
    _endpoint = 'admin/addresses'
    _resource = 'address'
