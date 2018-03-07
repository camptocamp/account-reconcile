# -*- coding: utf-8 -*-
# © 2015-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    active = fields.Boolean(
        'Active',
        default=True,
        help="The active field allows you to hide the purchase order "
             "without removing it."
    )

    partner_ref = fields.Char(
        states={'done': [('readonly', True)]},
    )

    validator = fields.Many2one(
        'res.users',
        string="Validated By",
        readonly=True
    )

    quantity_total = fields.Float(
        string='Total Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        store=True,
        readonly=True,
        compute='_compute_quantity_total'
    )

    @api.multi
    def button_approve(self):
        self.write({'validator': self.env.uid})
        return super(PurchaseOrder, self).button_approve()

    @api.depends('order_line.product_qty')
    def _compute_quantity_total(self):
        for order in self:
            order.quantity_total = sum(
                [line.product_qty for line in order.order_line]
            )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    _order = 'sequence asc, name asc'

    sequence = fields.Integer('Sequence')
