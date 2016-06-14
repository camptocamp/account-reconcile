# -*- coding: utf-8 -*-
from contextlib import closing, contextmanager
from support import *
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')


@contextmanager
def newcr(ctx):
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']

    registry = openerp.modules.registry.RegistryManager.new(db_name)
    with closing(registry.cursor()) as cr:
        try:
            yield cr
        except:
            cr.rollback()
            raise
        else:
            cr.commit()


@step('I delete all the {model_name} records created by uninstalled modules')
def impl(ctx, model_name):
    """
    Delete the records from `model_name` referenced by an entry in
    `ir.model.data` that is from an uninstalled module.

    Example of models that could be cleaned:
     ir.actions.act_window
     ir.actions.act_window.view
     ir.actions.client
     ir.actions.report.xml
     ir.actions.server
     ir.cron
     ir.rule
     ir.values
     ir.ui.menu
     ir.ui.view

    """
    modules = model('ir.module.module').browse(['state = installed'])
    module_names = [m.name for m in modules]
    entries = model('ir.model.data').browse(
        [('module', 'not in', module_names),
         ('model', '=', model_name)]
    )

    with newcr(ctx) as cr:
        if model_name.startswith('ir.actions'):
            table = 'ir_actions'
            action_type = model_name
        else:
            table = model_name.replace('.', '_')
            action_type = None

        table_delete_ids = set()
        entry_delete_ids = set()
        for entry in entries:
            cr.execute("SELECT * FROM information_schema.tables "
                       "WHERE table_name = %s", (table,))
            if cr.fetchone():  # the table exists
                table_delete_ids.add(entry.res_id)
            entry_delete_ids.add(entry.id)
        ir_values = ['%s,%d' % (model_name, tid) for tid in table_delete_ids]
        if ir_values:
            cr.execute("DELETE FROM ir_values WHERE value in %s",
                       (tuple(ir_values),))
        if table_delete_ids:
            sql = "DELETE FROM %s WHERE id IN %%s" % table
            params = [tuple(table_delete_ids)]
            if action_type:
                sql += " AND type = %s"
                params.append(action_type)
            cr.execute(sql, params)
        if entry_delete_ids:
            cr.execute("DELETE FROM ir_model_data WHERE id IN %s",
                       (tuple(entry_delete_ids),))


@step('I delete the broken ir.values')
def impl(ctx):
    """ Remove ir.values referring to not existing actions """
    with newcr(ctx) as cr:
        # we'll maybe need to remove other types than
        # ir.actions.act_window
        cr.execute(
            "DELETE "
            "FROM ir_values v "
            "WHERE NOT EXISTS ( "
            " SELECT id FROM ir_act_window "
            " WHERE id = replace(v.value, 'ir.actions.act_window,', '')::int) "
            "AND key = 'action' "
            "AND value LIKE 'ir.actions.act_window,%' "
        )
