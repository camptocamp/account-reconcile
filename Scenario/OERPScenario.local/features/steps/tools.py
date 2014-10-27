import openerp
import csv
import os
import os.path as osp
import datetime as dt
import subprocess
from support import *

@given('I execute the SQL command')
def impl(ctx):
    assert_true(ctx.text)
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']
    if openerp.release.version_info < (8,):
        pool = openerp.modules.registry.RegistryManager.get(db_name)
        cr = pool.db.cursor()
    else:
        registry = openerp.modules.registry.RegistryManager.new(db_name)
        cr = registry.cursor()
    try:
        cr.autocommit(True)
        sql =  ctx.text.strip()
        if sql:
            cr.execute(sql)
            puts(cr.statusmessage)
        try:
            ctx.data['return'] = cr.fetchall()
        except Exception:
            # ProgrammingError: no results to fetch
            ctx.data['return'] = []
    finally:
        cr.close()