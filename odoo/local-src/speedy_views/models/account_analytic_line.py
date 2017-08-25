# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    so_line = fields.Many2one(index=True)

    def _get_sale_order_line(self, vals=None):
        _super = super(AccountAnalyticLine, self)
        result = _super._get_sale_order_line(vals=vals)
        # The search on sale.order.line loads a lot of records in prefetch for
        # lines, sale.order and res.partner (at least). It would be a large
        # performance hit the next time we need an attribute on one of these
        # model if we don't clear the prefetch.
        self.env.prefetch.clear()
        return result
