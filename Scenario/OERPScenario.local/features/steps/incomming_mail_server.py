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
