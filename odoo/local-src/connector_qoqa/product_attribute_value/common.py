# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaProductAttributeValue(models.Model):
    _name = 'qoqa.product.attribute.value'
    _inherit = 'qoqa.binding'
    _inherits = {'product.attribute.value': 'openerp_id'}
    _description = 'QoQa Product Attribute Value'

    openerp_id = fields.Many2one(comodel_name='product.attribute.value',
                                 string='Attribute Value',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    qoqa_bind_ids = fields.One2many(
        'qoqa.product.attribute.value',
        'openerp_id',
        string='Attribute Bindings',
        copy=False,
    )


@qoqa
class ProductAttributeValueAdapter(QoQaAdapter):
    _model_name = 'qoqa.product.attribute.value'
    _endpoint = 'admin/product_attributes'
    _resource = 'product_attribute'
