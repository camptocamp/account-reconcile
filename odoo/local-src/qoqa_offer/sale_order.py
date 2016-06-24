# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import date

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    offer_id = fields.Many2one(
        comodel_name='qoqa.offer',
        string='Offer',
        readonly=True,
        index=True,
        ondelete='restrict',
    )
    qoqa_shop_id = fields.Many2one(
        comodel_name='qoqa.shop',
        string='QoQa Shop',
        ondelete='restrict',
    )

    @api.multi
    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals['offer_id'] = self.offer_id.id
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    offer_position_id = fields.Many2one(
        comodel_name='qoqa.offer.position',
        string='Offer Position',
        readonly=True,
        index=True,
        ondelete='restrict',
    )

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        _super = super(SaleOrderLine, self)
        vals = _super._prepare_order_line_procurement(group_id=group_id)
        vals['offer_id'] = self.order_id.offer_id.id
        return vals
