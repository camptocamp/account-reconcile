# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

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
        index=True,
    )

    @api.multi
    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals['offer_id'] = self.offer_id.id
        return vals

    @api.onchange('qoqa_shop_id')
    def onchange_qoqa_shop_id(self):
        self.project_id = self.qoqa_shop_id.analytic_account_id
