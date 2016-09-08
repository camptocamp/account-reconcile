# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaProductAttribute(models.Model):
    _name = 'qoqa.product.attribute'
    _inherit = 'qoqa.binding'
    _inherits = {'product.attribute': 'openerp_id'}
    _description = 'QoQa Product Attribute'

    openerp_id = fields.Many2one(comodel_name='product.attribute',
                                 string='Attribute',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A product attribute can be exported only once on the same backend"),
    ]


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    qoqa_bind_ids = fields.One2many(
        'qoqa.product.attribute',
        'openerp_id',
        string='Attribute Bindings',
        copy=False,
    )


@qoqa
class ProductAttributeAdapter(QoQaAdapter):
    _model_name = 'qoqa.product.attribute'
    _endpoint = 'admin/product_attribute_categories'
    _resource = 'product_attribute_category'
