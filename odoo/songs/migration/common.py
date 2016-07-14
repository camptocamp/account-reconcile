# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


def column_exists(ctx, table, column):
    ctx.env.cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name=%s and column_name=%s
    """, (table, column))
    return bool(ctx.env.cr.fetchone())


def table_exists(ctx, table):
    ctx.env.cr.execute("""
        SELECT table_name
        FROM information_schema.columns
        WHERE table_name = %s
    """, (table,))
    return bool(ctx.env.cr.fetchone())
