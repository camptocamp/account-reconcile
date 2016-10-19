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
    ref = fields.Char(
        string='Ref',
        readonly=True,
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        readonly=True
    )
    qoqa_shop_id = fields.Many2one(
        comodel_name='qoqa.shop',
        string='Sell on',
        readonly=True,
    )
    active = fields.Boolean(default=True)

    @api.multi
    @api.depends('name', 'ref')
    def name_get(self):
        return [(offer.id, offer.display_name) for offer in self]

    @api.multi
    @api.depends('name', 'ref')
    def _compute_display_name(self):
        for offer in self:
            offer.display_name = u'[%s] %s' % (offer.ref, offer.name)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = ['|', ('ref', operator, name), ('name', operator, name)]
        offers = self.search(domain + args, limit=limit)
        return offers.name_get()

    @api.multi
    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders')
        action = action.read()[0]
        action['domain'] = str([('offer_id', 'in', self.ids)])
        return action
