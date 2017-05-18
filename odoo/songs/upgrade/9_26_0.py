# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def add_view_all_stocks_location(ctx):
    """ Add new "Tous les stocks" location to only get stock info from it """
    if ctx.env.ref('scenario.all_stock_location', raise_if_not_found=False):
        return

    old_location = ctx.env.ref('stock.stock_location_stock')
    Location = ctx.env['stock.location']
    new_location = Location.create({
        'name': 'Tous les stocks',
        'location_id': old_location.location_id.id,
        'usage': 'view',
        'company_id': ctx.env.ref('scenario.qoqa_ch').id,
        'active': True
    })
    ctx.env['ir.model.data'].create({
        'module': 'scenario',
        'name': 'all_stock_location',
        'model': 'stock.location',
        'res_id': new_location.id
    })
    old_location.write({
        'location_id': new_location.id
    })
    warehouse = ctx.env.ref('stock.warehouse0')
    warehouse.write({
        'view_location_id': new_location.id
    })


@anthem.log
def main(ctx):
    add_view_all_stocks_location(ctx)
