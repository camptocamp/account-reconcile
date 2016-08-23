# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, exceptions, _

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class QoqaProductProduct(models.Model):
    _name = 'qoqa.product.product'
    _inherit = 'qoqa.binding'
    _inherits = {'product.product': 'openerp_id'}
    _description = 'QoQa Product'

    openerp_id = fields.Many2one(comodel_name='product.product',
                                 string='Product',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A product can be exported only once on the same backend"),
    ]


class ProductProduct(models.Model):
    _inherit = 'product.product'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.product.product',
        inverse_name='openerp_id',
        string='QoQa Bindings',
        copy=False,
    )

    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)',
         'The Internal Reference must be unique')
    ]

    @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'default_code' not in default and self.default_code:
            default['default_code'] = self.default_code + _('-copy')
        return super(ProductProduct, self).copy_data(default)[0]

    @api.multi
    def create_binding(self):
        backend = self.env['qoqa.backend'].get_singleton()
        for record in self:
            if not record.qoqa_bind_ids:
                self.env['qoqa.product.product'].create({
                    'backend_id': backend.id,
                    'openerp_id': record.id,
                })

    @api.model
    def create(self, vals):
        if self.env.context.get('default_product_tmpl_id'):
            vals['product_tmpl_id'] = (
                self.env.context['default_product_tmpl_id']
            )
        record = super(ProductProduct, self).create(vals)
        if record.product_tmpl_id.qoqa_exportable:
            record.create_binding()
        return record

    @api.multi
    def write(self, vals):
        if 'active' in vals and not vals.get('active'):
            if any(product.mapped('qoqa_bind_ids.qoqa_id')
                   for product in self):
                raise exceptions.UserError(
                    _('A product has already been exported and cannot be '
                      'disabled. If you were trying to add a new variant, '
                      'you must add it manually on the template.')
                )
        return super(ProductProduct, self).write(vals)

    @api.constrains('attribute_value_ids')
    def _check_attribute_value_length(self):
        for record in self:
            for attribute_value in record.attribute_value_ids:
                attribute_value._check_name_length()


@qoqa
class QoQaProductAdapter(QoQaAdapter):
    _model_name = 'qoqa.product.product'
    _endpoint = 'admin/variations'
    _resource = 'variation'
