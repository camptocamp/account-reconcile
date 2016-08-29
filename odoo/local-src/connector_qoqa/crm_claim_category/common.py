# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


class CrmClaimCategory(models.Model):
    _inherit = 'crm.claim.category'

    qoqa_id = fields.Char(string='ID on QoQa', index=True, copy=False)


@qoqa
class CrmClaimCategoryBinder(QoQaDirectBinder):
    _model_name = 'crm.claim.category'
