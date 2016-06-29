# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api, exceptions, _

from openerp.addons.connector.session import ConnectorSession

from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa
from .importer import import_product_images


class QoqaProductTemplate(models.Model):
    _name = 'qoqa.product.template'
    _inherit = 'qoqa.binding'
    _inherits = {'product.template': 'openerp_id'}
    _description = 'QoQa Template'

    openerp_id = fields.Many2one(comodel_name='product.template',
                                 string='Template',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A product template can be exported only once on the same backend"),
    ]

    @api.multi
    def import_images(self):
        session = ConnectorSession.from_env(self.env)
        for template in self:
            import_product_images(session, self._name,
                                  template.backend_id.id,
                                  template.qoqa_id)

    @api.model
    def create(self, vals):
        record = super(QoqaProductTemplate, self).create(vals)
        record.openerp_id.product_variant_ids.create_binding()
        return record

    @api.multi
    def unlink(self):
        for variant in self.mapped('openerp_id.product_variant_ids'):
            variant.qoqa_bind_ids.unlink()
        return super(QoqaProductTemplate, self).unlink()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.product.template',
        inverse_name='openerp_id',
        string='QoQa Bindings',
        copy=False,
    )
    qoqa_exportable = fields.Boolean(
        string='Exportable on QoQa',
        compute='_compute_qoqa_exportable',
    )

    @api.depends('qoqa_bind_ids')
    def _compute_qoqa_exportable(self):
        for record in self:
            record.qoqa_exportable = bool(record.qoqa_bind_ids)

    @api.multi
    def toggle_qoqa_exportable(self):
        for record in self:
            if record.qoqa_exportable:
                if any(record.mapped('qoqa_bind_ids.qoqa_id')):
                    raise exceptions.UserError(
                        _('Template already exported, it cannot be undone.')
                    )
                record.qoqa_bind_ids.unlink()
                record.mapped('product_variant_ids.qoqa_bind_ids').unlink()
            else:
                backend = self.env['qoqa.backend'].get_singleton()
                self.env['qoqa.product.template'].create({
                    'backend_id': backend.id,
                    'openerp_id': record.id,
                })


@qoqa
class QoQaTemplateAdapter(QoQaAdapter):
    _model_name = 'qoqa.product.template'
    _endpoint = 'admin/products'
    _resource = 'product'
