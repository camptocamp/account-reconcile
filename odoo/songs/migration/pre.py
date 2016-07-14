# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from common import column_exists, table_exists


def reset_modules_state(ctx):
    """ Reset 'state' of ir_module_module

    When we receive the database from the migration service, addons are
    'to upgrade', set them to uninstalled.
    """
    ctx.env.cr.execute("""
        UPDATE ir_module_module
        SET state = 'uninstalled'
        WHERE state IN ('to install', 'to upgrade')
    """)


def cron_no_doall(ctx):
    """ Remove the 'retry missing' flag on cron

    To avoid having them running again and again.
    """
    ctx.env.cr.execute("UPDATE ir_cron SET doall = false WHERE doall = true")


def _clean_uninstalled_model(ctx, model_name):
    env = ctx.env
    modules = env['ir.module.module'].search([('state', '=', 'installed')])
    module_names = [m.name for m in modules]
    entries = env['ir.model.data'].search(
        [('module', 'not in', module_names),
         ('model', '=', model_name)]
    )

    if model_name.startswith('ir.actions'):
        table = 'ir_actions'
        action_type = model_name
    else:
        table = model_name.replace('.', '_')
        action_type = None

    table_delete_ids = set()
    entry_delete_ids = set()
    cr = env.cr
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


def _clean_broken_ir_values(ctx):
    """ Remove ir.values referring to not existing actions """
    ctx.env.cr.execute(
        "DELETE "
        "FROM ir_values v "
        "WHERE NOT EXISTS ( "
        " SELECT id FROM ir_act_window "
        " WHERE id = replace(v.value, 'ir.actions.act_window,', '')::int) "
        "AND key = 'action' "
        "AND value LIKE 'ir.actions.act_window,%' "
    )


def clean_uninstalled(ctx):
    """ Clean technical records of uninstalled addons """
    models = (
        'ir.ui.view',
        'assembled.report',
        'ir.actions.act_window',
        'ir.actions.act_window.view',
        'ir.actions.client',
        'ir.actions.report.xml',
        'ir.actions.server',
        'ir.cron',
        'ir.rule',
        'ir.ui.menu',
        'ir.values',
    )
    for model_name in models:
        _clean_uninstalled_model(ctx, model_name)
    _clean_broken_ir_values(ctx)


def move_wine_ch_xml_ids(ctx):
    """ Move wine_ch_report xmlids to qoqa_product """
    ctx.env.cr.execute("""
        UPDATE ir_model_data SET module = 'qoqa_product'
        WHERE module = 'wine_ch_report'
        AND model in ('wine.class', 'wine.bottle')
    """)


def fix_claim_line_origin(ctx):
    """ A required field 'claim_origin' has been added and is empty """
    if not column_exists(ctx, 'claim_line', 'claim_origin'):
        ctx.env.cr.execute("""
            ALTER TABLE claim_line ADD COLUMN claim_origin varchar
        """)
    ctx.env.cr.execute("""
        UPDATE claim_line SET claim_origin = claim_origine
        WHERE claim_origine IS NOT NULL AND claim_origin IS NULL
    """)


def claim_rma(ctx):
    """ crm_claim.number has been renamed to crm_claim.code """
    if not column_exists(ctx, 'crm_claim', 'code'):
        ctx.env.cr.execute("""
            ALTER TABLE crm_claim ADD COLUMN code varchar
        """)
    ctx.env.cr.execute("""
        UPDATE crm_claim SET code = number
        WHERE number IS NOT NULL AND code != number
    """)
    ctx.env.cr.execute("""
        UPDATE mail_template
        SET body_html = REPLACE(body_html, 'object.number', 'object.code')
        WHERE model_id = (SELECT id FROM ir_model where model = 'crm.claim')
        AND body_html like '%object.number%';
    """)
    ctx.env.cr.execute("""
        UPDATE ir_translation
        SET value = REPLACE(value, 'object.number', 'object.code')
        WHERE name IN ('mail.template,body_html', 'mail.template,subject')
        AND value like '%object.number%'
        AND res_id IN (
          SELECT id FROM mail_template
          WHERE model_id = (SELECT id FROM ir_model where model = 'crm.claim')
        )
    """)
    # this fields has been renamed to 'code' in 'crm_claim_rma' but the
    # field with the old name is still present...
    ctx.env.cr.execute("""
        DELETE FROM ir_model_fields
        WHERE id = (
          SELECT res_id FROM ir_model_data
          WHERE model = 'ir.model.fields'
          AND name = 'field_crm_claim_number'
        )
    """)
    ctx.env.cr.execute("""
        DELETE FROM ir_model_data
        WHERE model = 'ir.model.fields'
        AND name = 'field_crm_claim_number'
    """)


def fix_claim_rma_update(ctx):
    """ lines in a wizard make the upgrade fail """
    ctx.env.cr.execute("""
        DELETE FROM claim_make_picking_wizard
    """)
    ctx.env.cr.execute("""
        UPDATE ir_model_data SET name = 'team_after_sales_service'
        WHERE name = 'section_after_sales_service' AND model = 'crm.team';
    """)


def connector_shipper_rate_rename(ctx):
    """ rename rate to fee in connector binding """
    if table_exists(ctx, 'qoqa_shipper_fee'):
        return
    ctx.env.cr.execute("""
        ALTER TABLE qoqa_shipper_rate RENAME TO qoqa_shipper_fee
    """)
    ctx.env.cr.execute("""
        ALTER SEQUENCE qoqa_shipper_rate_id_seq
        RENAME TO qoqa_shipper_fee_id_seq
    """)
    ctx.env.cr.execute("""
        SELECT i.relname as indname
        FROM   pg_index as idx
        JOIN   pg_class as i
        ON     i.oid = idx.indexrelid
        WHERE  i.relname LIKE '%qoqa_shipper_rate%'
    """)
    for index_name, in ctx.env.cr.fetchall():
        query = "ALTER INDEX %s RENAME TO %s" % (
            index_name,
            index_name.replace('qoqa_shipper_rate', 'qoqa_shipper_fee')
        )
        ctx.env.cr.execute(query)
    ctx.env.cr.execute("""
        SELECT
           constraint_name, table_name
        FROM
            information_schema.table_constraints
        WHERE constraint_type = 'FOREIGN KEY'
        AND   constraint_name LIKE '%qoqa_shipper_rate%';
    """)
    for constraint_name, table_name in ctx.env.cr.fetchall():
        query = ("""
            ALTER TABLE %s
            RENAME CONSTRAINT %s
            TO %s
        """) % (table_name,
                constraint_name,
                constraint_name.replace('qoqa_shipper_rate',
                                        'qoqa_shipper_fee')
                )
        ctx.env.cr.execute(query)


def main(ctx):
    """ Executed at the very beginning of the migration """
    reset_modules_state(ctx)
    cron_no_doall(ctx)
    clean_uninstalled(ctx)
    move_wine_ch_xml_ids(ctx)
    fix_claim_line_origin(ctx)
    claim_rma(ctx)
    fix_claim_rma_update(ctx)
    connector_shipper_rate_rename(ctx)
