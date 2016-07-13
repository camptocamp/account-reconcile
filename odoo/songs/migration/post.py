# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from . import post_product


def sale_shop(ctx):
    """ Migrate sale.shop to qoqa.shop """
    ctx.env.cr.execute("""
        UPDATE qoqa_shop q
        SET name = s.name,
            company_id = s.company_id,
            analytic_account_id = s.project_id,
            swiss_pp_logo = s.swiss_pp_logo,
            postlogistics_logo = s.postlogistics_logo,
            mail_signature_template = s.mail_signature_template
        FROM sale_shop s
        WHERE s.id = q.openerp_id
    """)
    ctx.env.cr.execute("""
        UPDATE crm_claim c
        SET qoqa_shop_id = q.id
        FROM qoqa_shop q
        WHERE q.openerp_id = c.shop_id
        AND shop_id IS NOT NULL AND qoqa_shop_id IS NULL
    """)
    ctx.env.cr.execute("""
        UPDATE sale_order c
        SET qoqa_shop_id = q.id
        FROM qoqa_shop q
        WHERE q.openerp_id = c.shop_id
        AND shop_id IS NOT NULL AND qoqa_shop_id IS NULL
    """)


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


def claim_sequence(ctx):
    """ Correct claim sequences """
    ctx.env.cr.execute("""
        UPDATE ir_sequence
        SET prefix = 'SOS-'
        WHERE code = 'crm.claim.rma.customer'
    """)
    copy_sequence_next_number(ctx, 'crm.claim.rma', 'crm.claim.rma.customer')


def payment_method(ctx):
    """ migrate payment.method → account.payment.mode """
    ctx.env.cr.execute("""
        INSERT INTO account_payment_mode (
          create_uid, write_uid, create_date, write_date,
          name, company_id, active, bank_account_link,
          fixed_journal_id, payment_method_id, workflow_process_id,
          days_before_cancel, import_rule, sequence,
          payment_cancellable_on_qoqa, qoqa_id,
          gift_card, payment_settlable_on_qoqa
          )
          SELECT
          create_uid, write_uid, create_date, write_date,
          name, COALESCE(company_id, 3), active, 'fixed',
          journal_id, 1, workflow_process_id,
          days_before_cancel, import_rule, sequence,
          payment_cancellable_on_qoqa, qoqa_id,
          gift_card, payment_settlable_on_qoqa
          FROM payment_method
          WHERE NOT EXISTS (SELECT id FROM account_payment_mode
                            WHERE name = payment_method.name)
    """)
    ctx.env.cr.execute("""
        UPDATE sale_order s
        SET payment_mode_id = m.id
        FROM account_payment_mode m
        INNER JOIN payment_method p
        ON p.name = m.name
        WHERE p.id = s.payment_method_id
        AND s.payment_method_id IS NOT NULL AND s.payment_mode_id IS NULL
    """)
    # trigger recomputation of function fields
    for mode in ctx.env['account.payment.mode'].search([]):
        mode.write({'payment_method_id': mode.payment_method_id.id})


def connector_qoqa(ctx):
    """ Migrate connector's stuff """
    ctx.env.cr.execute("""
      UPDATE qoqa_backend_timestamp
      SET from_date_field = 'import_discount_accounting_from_date'
      WHERE from_date_field = 'import_accounting_issuance_from_date'
    """)
    ctx.env.cr.execute("""
      INSERT INTO qoqa_backend_timestamp (backend_id, from_date_field,
                                          import_start_time)
      SELECT 1, 'import_crm_claim_from_date', '2016-06-15 00:00:00'
      WHERE NOT EXISTS (
        SELECT id FROM qoqa_backend_timestamp
        WHERE backend_id = 1
        AND from_date_field = 'import_crm_claim_from_date'
      )
    """)


def mail_alias(ctx):
    """ Rename 'shop_id' field in aliases' default values """
    cr = ctx.env.cr
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


def fix_journal_ids(ctx):
    # (old, new)
    mapping = [(4, 2),
               (5, 3),
               (12, 10),
               (13, 11),
               ]
    for old_id, new_id in mapping:
        ctx.env.cr.execute("""
            UPDATE account_invoice SET journal_id = %s
            WHERE journal_id = %s
        """, (new_id, old_id))
        ctx.env.cr.execute("""
            UPDATE account_move SET journal_id = %s
            WHERE journal_id = %s
        """, (new_id, old_id))
        ctx.env.cr.execute("""
            UPDATE account_move_line SET journal_id = %s
            WHERE journal_id = %s
        """, (new_id, old_id))
    ctx.env.cr.execute("""
          DELETE FROM account_journal WHERE id IN %s
    """, (tuple([m[0] for m in mapping]),))


def main(ctx):
    post_product.product_attribute_variants(ctx)
    post_product.product_brand(ctx)
    post_product.product_attributes(ctx)
    post_product.activate_variants(ctx)
    sale_shop(ctx)
    claim_sequence(ctx)
    payment_method(ctx)
    connector_qoqa(ctx)
    mail_alias(ctx)
    fix_journal_ids(ctx)
