# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    offer_id = fields.Many2one(
        comodel_name='qoqa.offer',
        string='Offer',
        readonly=True,
        index=True,
        ondelete='restrict',
    )
    sale_create_date = fields.Datetime(
        string='Sale Create Date',
        readonly=True,
    )

    # TODO: no longer invoice from pickings?
    # def _prepare_invoice(self, cr, uid, picking, partner, inv_type,
    #                      journal_id, context=None):
    #     vals = super(stock_picking, self)._prepare_invoice(
    #         cr, uid, picking, partner, inv_type, journal_id, context=context)
    #     if picking.offer_id:
    #         vals['offer_id'] = picking.offer_id.id
    #     return vals


class StockMove(models.Model):
    _inherit = 'stock.move'

    offer_id = fields.Many2one(
        related='picking_id.offer_id',
        readonly=True,
        store=True,
        index=True,
    )

    @api.model
    def _prepare_picking_assign(self, move):
        """ Prepares a new picking for this move as it could not be assigned to
        another picking. This method is designed to be inherited.
        """
        values = super(StockMove, self)._prepare_picking_assign(move)
        if move.procurement_id.sale_line_id:
            sale = move.procurement_id.sale_line_id.order_id
            values.update({
                'offer_id': sale.offer_id.id,
                'sale_create_date': sale.create_date
            })
        return values
