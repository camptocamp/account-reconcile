# -*- coding: utf-8 -*-
from support import *
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')


@step('I set the attribute model to {model_domain}')
def impl(ctx, model_domain):
    """
    Configure the model of an attribute (can't use the model_id in the table).
    """
    search_values = parse_domain(model_domain)
    search_domain = build_search_domain(ctx, 'ir.model', search_values)
    model_ids = model('ir.model').search(search_domain)
    assert model_ids
    values = {'model_id': model_ids[0]}
    # if ctx.found_item is not a dict, that's a record
    # and it already exist. We can't change the model of
    # an existing field, so we just skip the update
    if isinstance(ctx.found_item, dict):
        # that's a new attribute
        ctx.found_item.update(values)
