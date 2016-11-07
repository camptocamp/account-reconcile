# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


class QoqaCrmClaimCategory(models.Model):
    _name = 'qoqa.crm.claim.category'
    _inherit = 'qoqa.binding'
    _inherits = {'crm.claim.category': 'openerp_id'}
    _description = 'QoQa Claim Category'

    openerp_id = fields.Many2one(comodel_name='crm.claim.category',
                                 string='Claim Category',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')


class CrmClaimCategory(models.Model):
    _inherit = 'crm.claim.category'

    qoqa_id = fields.Char(string='ID on QoQa', index=True, copy=False)
    qoqa_bind_ids = fields.One2many(
        'qoqa.crm.claim.category',
        'openerp_id',
        string='Claim Categrory Bindings',
        copy=False,
        context={'active_test': False},
    )
