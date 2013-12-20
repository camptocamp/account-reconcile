
@step('I set the version of the instance to the value of "{filename}"')
def impl(ctx, filename):
    version = open(filename).read()
    set_version(ctx, version)

@step('I set the version of the instance to "{version}"')
def set_version(ctx, version):
    val = {'key': 'c2c.instance.version',
           'value': version}
    ids = model('ir.config_parameter').search([('key', '=', 'c2c.instance.version')])
    if ids:
        model('ir.config_parameter').write(ids, val)
    else:
        model('ir.config_parameter').create(val)

