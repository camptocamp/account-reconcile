# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from openerp import api, fields, models
from openerp.addons.connector_ecommerce.models.event import on_picking_out_done

_logger = logging.getLogger(__name__)


class QoqaStockPicking(models.Model):
    _name = 'qoqa.stock.picking'
    _inherit = 'qoqa.binding'
    _inherits = {'stock.picking': 'openerp_id'}
    _description = 'QoQa Delivery Order'

    openerp_id = fields.Many2one(comodel_name='stock.picking',
                                 string='Delivery Order',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    qoqa_sale_binding_id = fields.Many2one(
        'qoqa.sale.order',
        string='QoQa Sale Order',
        ondelete='set null',
    )
    exported = fields.Boolean('Exported')

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A delivery order can be exported only once on the same backend"),
    ]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.stock.picking',
        inverse_name='openerp_id',
        string='QBindings for Delivery Orders',
        copy=False,
        context={'active_test': False},
    )

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if vals.get('batch_picking_id'):
            self.mapped('sale_id').create_disable_address_change_job()
        return res

    @api.multi
    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if vals.get('batch_picking_id'):
            self.mapped('sale_id').create_disable_address_change_job()
        return res

    @api.multi
    def generate_labels(self, package_ids=None):
        res = super(StockPicking, self).generate_labels(package_ids)
        if not self.env.context.get('__called_from_batch_picking'):
            self.mapped('sale_id').create_disable_address_change_job()
        return res


@on_picking_out_done
def picking_done_create_binding(session, model_name, record_id,
                                picking_method):
    """ Create a binding for the picking so it will be exported. """
    picking = session.env[model_name].browse(record_id)
    sale = picking.sale_id
    if not sale:
        return
    if not sale.qoqa_bind_ids:
        return  # does not comes from QoQa

    for sale_binding in sale.qoqa_bind_ids:
        session.env['qoqa.stock.picking'].create({
            'backend_id': sale_binding.backend_id.id,
            'openerp_id': picking.id,
            'qoqa_sale_binding_id': sale_binding.id,
        })


class DeliveryCarrierLabelGenerate(models.TransientModel):
    _inherit = 'delivery.carrier.label.generate'

    def _do_generate_labels(self, group):
        with api.Environment.manage():
            super(DeliveryCarrierLabelGenerate, self.with_context(
                __called_from_batch_picking=True,
            ))._do_generate_labels(group)
