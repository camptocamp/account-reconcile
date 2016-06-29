# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaResPartner(models.Model):
    _name = 'qoqa.res.partner'
    _inherit = 'qoqa.binding'
    _inherits = {'res.partner': 'openerp_id'}
    _description = 'QoQa User'

    openerp_id = fields.Many2one(comodel_name='res.partner',
                                 string='Customer',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    qoqa_name = fields.Char(string='QoQa Name')
    qoqa_active = fields.Boolean(string='QoQa Active')
    created_at = fields.Datetime(string='Created At (on QoQa)')
    updated_at = fields.Datetime(string='Updated At (on QoQa)')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.res.partner',
        inverse_name='openerp_id',
        copy=False,
        string='QBindings')


@qoqa
class ResPartnerAdapter(QoQaAdapter):
    _model_name = 'qoqa.res.partner'
    _endpoint = 'admin/users'
    _resource = 'user'
