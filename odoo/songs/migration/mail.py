# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function

import time

from .common import table_exists


def verbose_execute(ctx, query, params=None):
    print(ctx.env.cr.mogrify(query, params))
    start = time.time()
    ctx.env.cr.execute(query, params)
    end = time.time()
    print('Duration: %s' % (end - start))


def mail_message_purge(ctx):
    start = time.time()
    if table_exists(ctx, 'mail_message_to_remove'):
        ctx.env.cr.execute("DROP TABLE mail_message_to_remove")

    # duration: 15-30s
    verbose_execute(ctx, """
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
    verbose_execute(ctx, """
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
        verbose_execute(ctx, "DROP index %s" % index_name)

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
        verbose_execute(ctx, """
            ALTER TABLE %s DROP CONSTRAINT %s
        """ % (table, constraint_name))

    verbose_execute(ctx, """
        SET temp_buffers = '1000MB'
    """)

    # duration: 60s
    verbose_execute(ctx, """
        CREATE TEMP TABLE tmp AS
        SELECT m.*
        FROM mail_message m
        LEFT JOIN mail_message_to_remove r USING (id)
        WHERE r.id IS NULL
    """)

    # duration: 0.0132989883423 :)
    verbose_execute(ctx, """
        TRUNCATE mail_message
    """)

    # duration: 90s
    verbose_execute(ctx, """
        INSERT INTO mail_message
        SELECT * from tmp
    """)

    for table, constraint_name, field, ondelete in referenced_by:
        # duration for delete + constraint: 30s * 10
        verbose_execute(ctx, """
            DELETE FROM %s
            WHERE %s IN (SELECT id FROM mail_message_to_remove)
        """ % (table, field))

        verbose_execute(ctx, """
            ALTER TABLE %s ADD CONSTRAINT %s FOREIGN KEY (%s)
            REFERENCES mail_message (id) ON DELETE %s
        """ % (table, constraint_name, field, ondelete))

    for index_name, fields in indices:
        # duration: 1-40s per index
        verbose_execute(ctx, """
            CREATE INDEX %s ON mail_message (%s)
        """ % (index_name, fields))

    # duration: negligible
    verbose_execute(ctx, """
        ANALYZE mail_message
    """)

    verbose_execute(ctx, """
        DROP TABLE mail_message_to_remove
    """)

    stop = time.time()
    print('purge of mail.message, total time: %s s' % (stop - start,))
