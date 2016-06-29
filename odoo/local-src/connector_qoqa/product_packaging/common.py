# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import models, fields
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    qoqa_id = fields.Char(string='ID on QoQa', index=True, copy=False)


@qoqa
class ProductPackagingBinder(QoQaDirectBinder):
    _model_name = 'product.packaging'
