# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from support import *
from support.tools import model


@given('I recompute the function fields of the payment modes')
def impl(ctx):
    for mode in model('account.payment.mode').browse([]):
        mode.write({'payment_method_id': mode.payment_method_id.id})
