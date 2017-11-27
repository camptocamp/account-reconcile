# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import anthem


@anthem.log
def update_stock_location_partners(ctx):
    """ Update stock locations to use the correct addresses """
    partners = ctx.env['res.partner'].search([('id', 'in', [8, 673201])])
    if len(partners) != 2:
        return

    if ctx.env.ref('stock.stock_location_stock', raise_if_not_found=False):
        ctx.env.ref('stock.stock_location_stock').partner_id = 673201
    if ctx.env.ref('__export__.stock_location_211', raise_if_not_found=False):
        ctx.env.ref('__export__.stock_location_211').partner_id = 8


@anthem.log
def main(ctx):
    update_stock_location_partners(ctx)
