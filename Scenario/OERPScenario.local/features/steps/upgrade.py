from support import *
import os.path as osp
import os
import datetime as dt
import subprocess


@step(u'I back up the database to "{dump_directory}"')
def impl(ctx, dump_directory):
    db_name = ctx.conf.get('db_name')
    if not osp.isdir(dump_directory):
        os.makedirs(dump_directory)
    filename = osp.join(dump_directory,
                        "%s_%s.dump" % (db_name,
                                        dt.datetime.now().strftime('%Y%m%d_%H%M%S'))
                            )
    cmd = ['pg_dump', '--no-owner',
           '--file', filename.encode('utf-8')]
    if ctx.conf.get('db_user'):
        cmd += ['--username', ctx.conf.get('db_user')]
    if ctx.conf.get('db_host'):
        cmd += ['--host', ctx.conf.get('db_host')]
    if ctx.conf.get('db_port'):
        cmd += ['--port', str(ctx.conf.get('db_port'))]
    cmd.append(db_name)
    env = os.environ.copy()
    if ctx.conf.get('db_password'):
        env['PGPASSWORD'] = ctx.conf.get('db_password')
    try:
        output = subprocess.check_call(cmd, env=env)
        #output = subprocess.check_output(cmd, env=env)
    except subprocess.CalledProcessError, exc:
        #output = exc.output
        #puts(output)
        raise
