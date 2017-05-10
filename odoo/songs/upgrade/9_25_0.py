# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def update_carrier_price_rules(ctx):
    """ Create default price rules for carriers """
    Carrier = ctx.env['delivery.carrier']
    carriers = Carrier.search([])
    for carrier in carriers:
        carrier.create_price_rules()


@anthem.log
def main(ctx):
    update_carrier_price_rules(ctx)
