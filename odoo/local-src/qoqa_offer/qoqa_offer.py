# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import division
from openerp import models, fields, api


class QoqaOffer(models.Model):
    _name = 'qoqa.offer'
    _description = 'QoQa Offer'

    name = fields.Char(
        string='Title',
        readonly=True,
    )
    qoqa_shop_id = fields.Many2one(
        comodel_name='qoqa.shop',
        string='Sell on',
        readonly=True,
    )
    active = fields.Boolean(default=True)

    @api.multi
    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders')
        action = action.read()[0]
        action['domain'] = str([('offer_id', 'in', self.ids)])
        return action
