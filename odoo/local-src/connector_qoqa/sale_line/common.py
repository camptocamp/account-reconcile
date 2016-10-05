# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api


class QoqaSaleOrderLine(models.Model):
    _name = 'qoqa.sale.order.line'
    _inherit = 'qoqa.binding'
    _inherits = {'sale.order.line': 'openerp_id'}
    _description = 'QoQa Sales Order Line'

    openerp_id = fields.Many2one(comodel_name='sale.order.line',
                                 string='Sales Order Line',
                                 required=True,
                                 index=True,
                                 ondelete='restrict')
    qoqa_order_id = fields.Many2one(comodel_name='qoqa.sale.order',
                                    string='QoQa Sale Order',
                                    required=True,
                                    readonly=True,
                                    ondelete='cascade',
                                    index=True)
    qoqa_quantity = fields.Integer(string='Quantity')
    discount_code_name = fields.Char()
    discount_description = fields.Char()

    _sql_constraints = [
        ('openerp_uniq', 'unique(backend_id, openerp_id)',
         "A sales order line can be exported only once on the same backend"),
    ]

    @api.model
    def create(self, vals):
        vals = vals.copy()
        qoqa_order_id = vals['qoqa_order_id']
        sale_binding_model = self.env['qoqa.sale.order']
        sale_binding = sale_binding_model.browse(qoqa_order_id)
        order = sale_binding.openerp_id
        vals['order_id'] = order.id
        return super(QoqaSaleOrderLine, self).create(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qoqa_bind_ids = fields.One2many(
        comodel_name='qoqa.sale.order.line',
        inverse_name='openerp_id',
        string='QBindings',
        context={'active_test': False},
    )
