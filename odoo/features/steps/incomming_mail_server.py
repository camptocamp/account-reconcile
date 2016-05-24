# -*- coding: utf-8 -*-
from support import *
import logging

logger = logging.getLogger('openerp.behave')


@step('I test and confirm the incomming mail server')
def impl(ctx):
    assert ctx.found_item
    assert ctx.found_item.id
    incomming_server = ctx.found_item
    incomming_server.button_confirm_login()

@step('I setup the shop to "{shopname}"')
def impl(ctx, shopname):
    assert ctx.found_item
    assert ctx.found_item.id
    alias = ctx.found_item
    SaleShop = model('sale.shop')
    Alias = model('mail.alias')
    shop = SaleShop.browse([('name','=',shopname)])
    assert shop
    build_def_values = "{'shop_id':" + str(shop[0].id) + "}"
    ctx.found_item.write({'alias_defaults':build_def_values})
    # Alias.write(ctx.found_item, {'alias_defaults':build_def_values})
