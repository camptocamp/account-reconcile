# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem

from ..common import table_exists


@anthem.log
def mail_message_purge(ctx):
    """ Purging mail_message records """
    if table_exists(ctx, 'mail_message_to_remove'):
        ctx.env.cr.execute("DROP TABLE mail_message_to_remove")

    # duration: 15-30s
    with ctx.log(u'creating a table with mail_message ids to remove'):
        ctx.env.cr.execute("""
            CREATE TABLE mail_message_to_remove AS
              SELECT id FROM mail_message
              WHERE (model in ('sale.order',
                               'account.invoice',
                               'stock.picking',
                               'res.partner',
                               'account.bank.statement',
                               'procurement.order')
                     AND message_type = 'notification')
                 OR model in ('queue.job',
                               'qoqa.offer',
                               'account.statement.profile',
                               'account.easy.reconcile')
        """)
    # ~5000 messages have a parent_id which would be deleted,
    # keep them, that's the easy way, but a bit slow :-(
    # duration: 150s
    with ctx.log(u'removing from this table some ids to keep because '
                 u'they are used by other messages'):
        ctx.env.cr.execute("""
            DELETE FROM mail_message_to_remove WHERE id IN (
                SELECT parent_id
                FROM mail_message m
                LEFT JOIN mail_message_to_remove r USING (id)
                INNER JOIN mail_message_to_remove p
                ON p.id = m.parent_id
                WHERE r.id IS NULL
            )
        """)
    # all indices but the PK
    indices = [
        ('mail_message_author_id_index', 'author_id'),
        ('mail_message_message_id_index', 'message_id'),
        ('mail_message_model_index', 'model'),
        ('mail_message_model_res_id_idx', 'model, res_id'),
        ('mail_message_parent_id_index', 'parent_id'),
        ('mail_message_res_id_index', 'res_id'),
        ('mail_message_subtype_id_index', 'subtype_id'),
    ]

    for index_name, __ in indices:
        ctx.env.cr.execute("DROP index %s" % index_name)

    # referenced by:
    referenced_by = [
        ('mail_channel_partner',
         'mail_channel_partner_seen_message_id_fkey',
         'seen_message_id',
         'SET NULL'),
        ('mail_compose_message',
         'mail_compose_message_parent_id_fkey',
         'parent_id',
         'SET NULL'),
        ('mail_mail',
         'mail_mail_mail_message_id_fkey',
         'mail_message_id',
         'CASCADE'),
        ('mail_message_mail_channel_rel',
         'mail_message_mail_channel_rel_mail_message_id_fkey',
         'mail_message_id',
         'CASCADE'),
        ('mail_message_res_partner_needaction_rel',
         'mail_message_res_partner_needaction_rel_mail_message_id_fkey',
         'mail_message_id',
         'CASCADE'),
        ('mail_message_res_partner_rel',
         'mail_message_res_partner_rel_mail_message_id_fkey',
         'mail_message_id',
         'CASCADE'),
        ('mail_message_res_partner_starred_rel',
         'mail_message_res_partner_starred_rel_mail_message_id_fkey',
         'mail_message_id',
         'CASCADE'),
        ('mail_tracking_value',
         'mail_tracking_value_mail_message_id_fkey',
         'mail_message_id',
         'CASCADE'),
        ('message_attachment_rel',
         'message_attachment_rel_message_id_fkey',
         'message_id',
         'CASCADE'),
        ('mail_message',
         'mail_message_parent_id_fkey',
         'parent_id',
         'SET NULL'),
    ]

    for table, constraint_name, __, __ in referenced_by:
        ctx.env.cr.execute("""
            ALTER TABLE %s DROP CONSTRAINT %s
        """ % (table, constraint_name))

    ctx.env.cr.execute("""
        SET temp_buffers = '1000MB'
    """)

    # duration: 60s
    with ctx.log(u'creating a temporary table as a copy of mail_message '
                 u'records to keep'):
        ctx.env.cr.execute("""
            CREATE TEMP TABLE tmp AS
            SELECT m.*
            FROM mail_message m
            LEFT JOIN mail_message_to_remove r USING (id)
            WHERE r.id IS NULL
        """)

    # duration: 0.0132989883423 :)
    with ctx.log(u'truncating mail_message'):
        ctx.env.cr.execute("""
            TRUNCATE mail_message
        """)

    # duration: 90s
    with ctx.log(u'writing back mail_message records from the temp table '):
        ctx.env.cr.execute("""
            INSERT INTO mail_message
            SELECT * from tmp
        """)

    for table, constraint_name, field, ondelete in referenced_by:
        # duration for delete + constraint: 30s * 10
        with ctx.log(u're-creating constraint %s' % (constraint_name,)):
            ctx.env.cr.execute("""
                DELETE FROM %s
                WHERE %s IN (SELECT id FROM mail_message_to_remove)
            """ % (table, field))

            ctx.env.cr.execute("""
                ALTER TABLE %s ADD CONSTRAINT %s FOREIGN KEY (%s)
                REFERENCES mail_message (id) ON DELETE %s
            """ % (table, constraint_name, field, ondelete))

    for index_name, fields in indices:
        # duration: 1-40s per index
        with ctx.log(u're-creating index %s' % (index_name,)):
            ctx.env.cr.execute("""
                CREATE INDEX %s ON mail_message (%s)
            """ % (index_name, fields))

    # duration: negligible
    with ctx.log(u'analyzing mail_message'):
        ctx.env.cr.execute("""
            ANALYZE mail_message
        """)

    ctx.env.cr.execute("""
        DROP TABLE mail_message_to_remove
    """)
