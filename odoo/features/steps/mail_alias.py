# -*- coding: utf-8 -*-
import logging

from contextlib import closing, contextmanager
from support import *
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


@given('I correct the alias default values for shop_id')
def impl(ctx):
    with newcr(ctx) as cr:
        query = ("SELECT openerp_id, id "
                 "FROM qoqa_shop ")
        cr.execute(query)
        shop_mapping = dict(cr.fetchall())

        # convert shop_id to qoqa_shop_id
        query = ("SELECT id, alias_defaults "
                 "FROM mail_alias "
                 "WHERE alias_defaults LIKE '%''shop_id''%'")
        cr.execute(query)
        for alias_id, defaults in cr.fetchall():
            defaults = eval(defaults)
            old_shop_id = defaults.pop('shop_id')
            try:
                qoqa_shop_id = shop_mapping[old_shop_id]
            except KeyError:
                pass  # no matching shop for qoqa_shop, ignore
            else:
                defaults['qoqa_shop_id'] = qoqa_shop_id
            query = (
                "UPDATE mail_alias "
                "SET alias_defaults = %s "
                "WHERE id = %s "
            )
            params = (unicode(defaults), alias_id)
            cr.execute(query, params)

        # convert section_id to team_id
        query = ("SELECT id, alias_defaults "
                 "FROM mail_alias "
                 "WHERE alias_defaults LIKE '%''section_id''%'")
        cr.execute(query)
        for alias_id, defaults in cr.fetchall():
            defaults = eval(defaults)
            defaults['team_id'] = defaults.pop('section_id')
            query = (
                "UPDATE mail_alias "
                "SET alias_defaults = %s "
                "WHERE id = %s "
            )
            params = (unicode(defaults), alias_id)
            cr.execute(query, params)
