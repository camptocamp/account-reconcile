# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import _, api, models, exceptions, fields

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

    @api.constrains('name')
    def _check_name_length(self):
        for record in self:
            if not record.name:
                continue
            # This is a business request. We don't limit the 'size' on the
            # field because historic attribute values might be longer.
            # When an historic value is longer, we expect to have an error
            # so the user has to correct it.
            if len(record.name) > 25:
                raise exceptions.ValidationError(
                    _("The limit for an attribute value is 25 characters.\n"
                      "'%s' should therefore be shorter.") % (record.name,)
                )


@qoqa
class ProductAttributeValueAdapter(QoQaAdapter):
    _model_name = 'qoqa.product.attribute.value'
    _endpoint = 'admin/product_attributes'
    _resource = 'product_attribute'
