# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import openerp
from openerp import models, fields, api, exceptions, _

from openerp.addons.connector.session import ConnectorSession

from ..unit.backend_adapter import QoQaAdapter, api_handle_errors
from ..backend import qoqa
from .importer import import_product_images
from ..unit.deleter import export_delete_record


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
        if any(record.qoqa_id for record in self):
            raise exceptions.UserError(
                _('Template already exported, it cannot be undone.')
            )
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
        context={'active_test': False},
    )
    qoqa_exportable = fields.Boolean(
        string='Exportable on QoQa',
        compute='_compute_qoqa_exportable',
    )

    @api.multi
    def _delete_on_qoqa_shop(self):
        session = ConnectorSession.from_env(self.env)
        message = _('Impossible to disable the product, it is '
                    'used in an offer or it could not be deleted on '
                    'the backend.')
        with api_handle_errors(message):
            for binding in self.qoqa_bind_ids:
                export_delete_record(session, binding._name,
                                     binding.backend_id.id,
                                     binding.qoqa_id)
                binding.with_context(connector_no_export=True).qoqa_id = False

    @api.multi
    def _write_with_disable(self, vals):
        self.ensure_one()
        already_inactive = not self.active
        # we come from the write of this class, so we should not call it again,
        # but instead call the super one
        dbname = self.env.cr.dbname
        db_registry = openerp.modules.registry.RegistryManager.new(dbname)
        # use a new transaction, because if we are disabling more than
        # one record at a time, or doing other things in the main transaction
        # and there is failure, we'll lose the changes odoo's side, but the
        # change Q4's side will be committed... so to keep the delete in sync
        # we have to commit after every DELETE request sent to Q4
        with api.Environment.manage(), db_registry.cursor() as cr:
            env = self.env(cr=cr)
            template = self.with_env(env)
            super(ProductTemplate, template).write(vals)
            if already_inactive:
                return
            try:
                template._delete_on_qoqa_shop()
            except exceptions.UserError:
                raise

    @api.multi
    def write(self, vals):
        if 'active' in vals and not vals['active']:
            for template in self:
                template._write_with_disable(vals)
            return True
        else:
            return super(ProductTemplate, self).write(vals)

    @api.depends('qoqa_bind_ids')
    def _compute_qoqa_exportable(self):
        for record in self:
            record.qoqa_exportable = bool(record.qoqa_bind_ids)

    @api.multi
    def toggle_qoqa_exportable(self):
        for record in self:
            if record.qoqa_exportable:
                record.qoqa_bind_ids.unlink()
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
