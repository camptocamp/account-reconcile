# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaCrmClaim(models.Model):
    _name = 'qoqa.crm.claim'
    _inherit = 'qoqa.binding'
    _inherits = {'crm.claim': 'openerp_id'}
    _description = 'QoQa Claim'

    openerp_id = fields.Many2one(comodel_name='crm.claim',
                                 string='Claim',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    created_at = fields.Datetime(string='Created At (on QoQa)')
    updated_at = fields.Datetime(string='Updated At (on QoQa)')


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.crm.claim',
        inverse_name='openerp_id',
        copy=False,
        string='QBindings',
        context={'active_test': False},
    )


class QoQaClaimMedium(models.Model):
    _name = 'qoqa.crm.claim.medium'
    _inherit = 'qoqa.binding'
    _inherits = {'ir.attachment': 'openerp_id'}
    _description = 'QoQa Claim Medium'

    openerp_id = fields.Many2one(comodel_name='ir.attachment',
                                 string='Attachment',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    created_at = fields.Datetime(string='Created At (on QoQa)')
    updated_at = fields.Datetime(string='Updated At (on QoQa)')


@qoqa
class CrmClaimAdapter(QoQaAdapter):
    _model_name = 'qoqa.crm.claim'
    _endpoint = 'admin/claims'
    _resource = 'claim'
