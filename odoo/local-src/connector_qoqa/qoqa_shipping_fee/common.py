# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaShippingFee(models.Model):
    _name = 'qoqa.shipping.fee'
    _inherit = 'qoqa.binding'
    _description = 'QoQa Shipping Fees'

    name = fields.Char(required=True)
    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
        default=lambda self: self._default_product_id(),
    )
    account_tax = fields.Many2one(comodel_name='account.tax')

    @api.model
    def _default_product_id(self):
        product = self.env.ref('connector_ecommerce.product_product_shipping',
                               raise_if_not_found=False)
        return product.id


@qoqa
class ShippingFeeAdapter(QoQaAdapter):
    _model_name = 'qoqa.shipping.fee'
    _endpoint = 'admin/shipping_fees'
    _resource = 'shipping_fee'
