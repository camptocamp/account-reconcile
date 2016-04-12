# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import division
from openerp import models, fields, api, exceptions, _


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
        action = action.read()
        action['domain'] = str([('offer_id', 'in', self.ids)])
        return action

    def button_orderpoint(self, cr, uid, ids, context=None):
        raise NotImplementedError('not implemented')
        # TODO this button should be moved to products
        products = set()
        for offer in self.browse(cr, uid, ids, context=context):
            for position in offer.position_ids:
                for variant in position.variant_ids:
                    products.add(variant.product_id)
        orderpoint_ids = set()
        for product in products:
            for orderpoint in product.orderpoint_ids:
                orderpoint_ids.add(orderpoint.id)
        if not orderpoint_ids:
            raise exceptions.UserError(
                _('Error'),
                _('The products have no orderpoints configured.')
            )
        orderpoint_obj = self.pool['stock.warehouse.orderpoint']
        procurement_obj = self.pool['procurement.order']
        orderpoint_confirm = orderpoint_obj.procure_orderpoint_confirm
        procurement_ids = orderpoint_confirm(cr, uid, list(orderpoint_ids),
                                             context=context)
        purchase_ids = []
        procurements = procurement_obj.browse(cr, uid, procurement_ids,
                                              context=context)
        for procurement in procurements:
            if procurement.purchase_id:
                purchase_ids.append(procurement.purchase_id.id)
        return {
            'domain': "[('id', 'in', %s)]" % purchase_ids,
            'name': _('Generated Purchases'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
