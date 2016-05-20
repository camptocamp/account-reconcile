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

    # TODO: call in connector_qoqa with new API
    @api.onchange('position_id')
    def onchange_offer_position_id(self):
        """ Set the delivery delay of the line according to the offer position

        If a position has a delivery date, it is used to compute the
        number of days it takes to deliver. This number becomes the 'delay'
        of the line.

        This onchange is not used on the view actually, but is called
        in the connector_qoqa when calling the onchanges chain.
        """
        if not self.offer_position_id:
            return
        position = self.offer_position_id
        delivery_date = position.date_delivery
        if not delivery_date:
            return
        delivery_date = fields.Date.from_string(delivery_date)
        today = date.today()
        self.delay = (delivery_date - today).days
