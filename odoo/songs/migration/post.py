# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import print_function

import anthem

from . import post_dispatch
from . import post_product
from ..common import copy_sequence_next_number


@anthem.log
def sale_shop(ctx):
    """ Migrating sale.shop to qoqa.shop """
    with ctx.log(u'moving sale.shop values to qoqa.shop values'):
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
    with ctx.log(u'setting qoqa_shop_id on crm_claim'):
        ctx.env.cr.execute("""
            UPDATE crm_claim c
            SET qoqa_shop_id = q.id
            FROM qoqa_shop q
            WHERE q.openerp_id = c.shop_id
            AND shop_id IS NOT NULL AND qoqa_shop_id IS NULL
        """)
    with ctx.log(u'setting qoqa_shop_id on sale_order'):
        ctx.env.cr.execute("""
            UPDATE sale_order c
            SET qoqa_shop_id = q.id
            FROM qoqa_shop q
            WHERE q.openerp_id = c.shop_id
            AND shop_id IS NOT NULL AND qoqa_shop_id IS NULL
        """)


@anthem.log
def claim_sequence(ctx):
    """ Correcting claim sequences """
    ctx.env.cr.execute("""
        UPDATE ir_sequence
        SET prefix = 'SOS-'
        WHERE code = 'crm.claim.rma.customer'
    """)
    copy_sequence_next_number(ctx, 'crm.claim.rma', 'crm.claim.rma.customer')


@anthem.log
def payment_method(ctx):
    """ Migrating payment.method -> account.payment.mode """
    with ctx.log(u'creating account_payment_mode records'):
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
    with ctx.log(u'setting payment_mode_id on sale_order'):
        ctx.env.cr.execute("""
            UPDATE sale_order s
            SET payment_mode_id = m.id
            FROM account_payment_mode m
            INNER JOIN payment_method p
            ON p.name = m.name
            WHERE p.id = s.payment_method_id
            AND s.payment_method_id IS NOT NULL AND s.payment_mode_id IS NULL
        """)
    with ctx.log(u'setting payment_mode_id on account_invoice'):
        ctx.env.cr.execute("""
            UPDATE account_invoice i
            SET payment_mode_id = o.payment_mode_id
            FROM sale_order o
            INNER JOIN sale_order_line ol
            ON ol.order_id = o.id
            INNER JOIN sale_order_line_invoice_rel rel
            ON rel.order_line_id = ol.id
            INNER JOIN account_invoice_line il
            ON il.id = rel.invoice_line_id
            WHERE il.invoice_id = i.id
            AND i.payment_mode_id != o.payment_mode_id
        """)
    with ctx.log(u'trigger recomputation of function fields'):
        for mode in ctx.env['account.payment.mode'].search([]):
            mode.write({'payment_method_id': mode.payment_method_id.id})


@anthem.log
def connector_qoqa(ctx):
    """ Migrating connector's stuff """
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


@anthem.log
def mail_alias(ctx):
    """ Renaming 'shop_id' field in aliases' default values """
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


@anthem.log
def mail_template(ctx):
    """ Fixing reference to renamed fields in bodies of email templates """
    cr = ctx.env.cr
    # Remove user defaults
    query = "DELETE FROM ir_values WHERE model = 'mail.compose.message';"
    cr.execute(query)

    # Replace "shop_id" by "qoqa_shop_id" in mail templates
    query = (
        "UPDATE mail_template "
        "SET body_html = replace(body_html, 'object.shop_id', "
        "'object.qoqa_shop_id') "
        "WHERE body_html ~ 'object.shop_id'"
    )
    cr.execute(query)
    # Replace "shop_id" by "qoqa_shop_id" in mail templates in translations
    query = (
        "UPDATE ir_translation "
        "SET src = replace(src, 'object.shop_id', "
        "'object.qoqa_shop_id'), "
        "value = replace(value, 'object.shop_id', "
        "'object.qoqa_shop_id') "
        "WHERE src ~ 'object.shop_id' OR value ~ 'object.shop_id'"
    )
    cr.execute(query)

    # define default mail template
    MailTemplate = ctx.env['mail.template']
    template_name = "0 - Réponse vide"
    default_template = MailTemplate.search(
        [('name', '=', template_name)], limit=1)
    default_template.is_default = True


@anthem.log
def fix_journal_ids(ctx):
    """ Fix mapping of accounting journals """
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


@anthem.log
def configure_shipper_package_types(ctx):
    """ Configuring delivery carriers

    Disable qoqa shipper services not used anymore and configure
    the new 'package types'

    Based on
    https://docs.google.com/a/qoqa.com/spreadsheets/d/14qfCiFSvqnf_ZidqMbeljyx79BEq7IyjA3DjtVXpNTA/edit?usp=sharing

    """
    inactive = (65, 66, 68, 50, 61, 49, 48, 47, 46, 52, 45, 55)
    ctx.env.cr.execute("""
        UPDATE delivery_carrier SET active = false
        WHERE id IN %s
    """, (inactive,))
    mappings = [(125, 14),
                (77, 8),
                (67, 7),
                (60, 5),
                (59, 13),
                (58, 2),
                (57, 12),
                (56, 1),
                (54, 6),
                (53, 8),
                (44, 14),
                ]
    # just in case we run the migration script 2 times:
    ctx.env.cr.execute("""
        DELETE FROM qoqa_shipper_package_type
    """)
    check_query = "SELECT id FROM delivery_carrier WHERE id = %s"
    insert_query = ("""
            INSERT INTO qoqa_shipper_package_type
                (openerp_id, qoqa_id, backend_id,
                 create_uid, create_date,
                 write_uid, write_date)
            VALUES
                (%s, %s,
                 (SELECT id FROM qoqa_backend),
                 1, NOW(), 1, NOW())
    """)
    for carrier_id, qoqa_id in mappings:
        ctx.env.cr.execute(check_query, (carrier_id,))
        if ctx.env.cr.fetchone():
            ctx.env.cr.execute(insert_query, (carrier_id, qoqa_id))
        else:
            print('Could not create the qoqa_shipper_package_type with '
                  'qoqa_id %s because the delivery_carrier with id %s '
                  'is missing.' % (qoqa_id, carrier_id))


@anthem.log
def move_journal_import_setup(ctx):
    """ Moving journal import setup

    The configuration in account_statement_profile is now in account_journal
    """
    rules = [
        ctx.env.ref('account_move_transactionid_import.'
                    'bank_statement_completion_rule_4').id,
        ctx.env.ref('account_move_transactionid_import.'
                    'bank_statement_completion_rule_trans_id_invoice').id,
        ctx.env.ref('account_move_so_import.'
                    'bank_statement_completion_rule_1').id
    ]
    for journal in ctx.env['account.journal'].browse([51, 28, 27, 72, 76]):
        journal.used_for_import = True
        journal.used_for_completion = True
        journal.s3_import = True
        journal.rule_ids = rules
        ctx.env.cr.execute("""
            UPDATE account_journal j
            SET commission_account_id = p.commission_account_id,
                receivable_account_id = p.receivable_account_id,
                partner_id = p.partner_id,
                message_last_post = p.message_last_post,
                import_type = p.import_type,
                last_import_date = p.last_import_date,
                launch_import_completion = p.launch_import_completion
            FROM account_statement_profile p
            WHERE j.id = p.journal_id
            AND j.id = %s
        """, (journal.id, ))


@anthem.log
def main(ctx):
    """ Executing main entry point called after upgrade of addons """
    post_product.product_attribute_variants(ctx)
    post_product.product_brand(ctx)
    post_product.product_attributes(ctx)
    post_product.activate_variants(ctx)
    post_product.default_values(ctx)
    sale_shop(ctx)
    claim_sequence(ctx)
    payment_method(ctx)
    connector_qoqa(ctx)
    mail_alias(ctx)
    mail_template(ctx)
    fix_journal_ids(ctx)
    configure_shipper_package_types(ctx)
    move_journal_import_setup(ctx)
    post_dispatch.dispatch_migration(ctx)
