# -*- coding: utf-8 -*-


@step('we select users below, even the deactivated ones')
def impl(ctx):
    logins = [row['login'] for row in ctx.table]
    ctx.found_items = model('res.users').browse([('login', 'in', logins)],
                                                context={'active_test': False})
    assert_equal(len(ctx.found_items), len(logins))

@step('login with the admin user')
def impl(ctx):
    server = ctx.conf['server']
    admin_login_password = server.tools.config.get('admin_login_password')
    database = server.tools.config['db_name']
    if admin_login_password:
        ctx.client.login('admin', admin_login_password, database=database)
    else:
        ctx.client.login('admin', 'admin', database=database)
