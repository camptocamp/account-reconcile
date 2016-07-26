# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import pickle


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


def create_default_value(ctx, model, field, company_id, value):
    ctx.env.cr.execute("""
    INSERT INTO ir_values
        (name, model, value, key, key2, company_id, user_id)
    SELECT %(field)s, %(model)s, %(pickled)s, 'default', NULL,
           %(company_id)s, NULL
    WHERE NOT EXISTS (
      SELECT id FROM ir_values
      WHERE name = %(field)s
            AND model = %(model)s
            AND company_id = %(company_id)s
            AND user_id is NULL
            AND key = 'default' and key2 is NULL
    )
    """, {'field': field,
          'model': model,
          'company_id': company_id,
          'pickled': pickle.dumps(value),
          })


# TODO: candidate for a new anthem.lyrics?
def copy_sequence_next_number(ctx,
                              source_sequence_code,
                              target_sequence_code):
    Sequence = ctx.env['ir.sequence']
    source_sequence = Sequence.search([('code', '=', source_sequence_code)])
    target_sequence = Sequence.search([('code', '=', target_sequence_code)])
    target_sequence.write(
        {'number_next': source_sequence.number_next}
    )
