# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    qoqa_id = fields.Char(string='ID on QoQa', index=True, copy=False)


@qoqa
class CurrencyBinder(QoQaDirectBinder):
    _model_name = 'res.currency'
