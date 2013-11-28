# -*- coding: utf-8 -*-


@step('we select users below, even the deactivated ones')
def impl(ctx):
    logins = [row['login'] for row in ctx.table]
    ctx.found_items = model('res.users').browse([('login', 'in', logins)],
                                                context={'active_test': False})
    assert_equal(len(ctx.found_items), len(logins))
