# -*- coding: utf-8 -*-
from support import *
import logging

logger = logging.getLogger('openerp.behave')


@step('I set selection field "base" with {value}')
def impl(ctx, value):
    """
    Permits to set a "oid" to any kind of field
    """
    try:
        value = int(value)
    except ValueError:
        search_values = parse_domain(value)
        search_domain = build_search_domain(ctx, 'product.price.type', search_values)
        if search_domain:
            value = model('product.price.type').browse(search_domain).id[0]

    values = {'base': value}

    ctx.found_item.write(values)
