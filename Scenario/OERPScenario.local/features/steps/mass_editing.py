# -*- coding: utf-8 -*-
from support import *
from support.tools import model


@step('I add the field with oid {field_oid} to the mass editing')
def impl(ctx, field_oid):
    assert ctx.found_item
    assert ctx.found_item.id
    field = model('ir.model.fields').get(field_oid)
    values = {'field_ids': [(4, field.id)]}
    ctx.found_item.write(values)
