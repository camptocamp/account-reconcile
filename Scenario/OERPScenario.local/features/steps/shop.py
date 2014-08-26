# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger('openerp.behave')

@given(u'I set a postlogistics label logo from file "{logo_path}"')
def impl(ctx, logo_path):
    """
    Configure a logo for a shop.
    """
    assert ctx.found_item
    shop = ctx.found_item
    encoded_image = get_encoded_image(ctx, logo_path)
    shop.write({'postlogistics_logo': encoded_image})
