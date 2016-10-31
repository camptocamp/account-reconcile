# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update

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
    with ctx.log(u'updating the shops qoqa_id mapping'):
        mapping = [(1, 3), (2, 5), (3, 8), (4, 10), (5, 4), (6, 9), (7, 11),
                   (8, 14), (9, 15), (10, 16), (11, 17)]
        # prevent unique key constraint error
        ctx.env.cr.execute("UPDATE qoqa_shop SET qoqa_id = null")
        for shop_id, qoqa_id in mapping:
            ctx.env.cr.execute("""
                UPDATE qoqa_shop SET qoqa_id = %s
                WHERE id = %s
            """, (qoqa_id, shop_id))


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
              gift_card, payment_settlable_on_qoqa,
              refund_max_days, refund_min_date
              )
              SELECT
              create_uid, write_uid, create_date, write_date,
              name, COALESCE(company_id, 3), active, 'fixed',
              journal_id, 1, workflow_process_id,
              days_before_cancel, import_rule, sequence,
              payment_cancellable_on_qoqa, qoqa_id,
              gift_card, payment_settlable_on_qoqa,
              refund_max_days, refund_min_date
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
    with ctx.log(u'setting DTA payment modes on supplier invoices'):
        ctx.env.cr.execute("""
            UPDATE account_invoice
            SET payment_mode_id = NULL
            WHERE type = 'in_invoice';

            DELETE FROM account_payment_mode
            WHERE payment_method_code = 'DTA';

            DELETE FROM account_payment_method
            WHERE code = 'DTA';


            INSERT INTO account_payment_method (
                id, create_uid, write_uid, create_date, write_date, code,
                name, payment_type, display_name, bank_account_required,
                active
            ) VALUES (
                NEXTVAL('account_payment_method_id_seq'), 1, 1,
                current_timestamp, current_timestamp, 'DTA', 'DTA',
                'outbound', '[DTA] DTA (outbound)', True, True
            );


            INSERT INTO account_payment_mode (
                id, create_uid, write_uid, create_date, write_date, name,
                company_id, bank_account_link, payment_method_code,
                fixed_journal_id, payment_type, active, payment_method_id,
                default_invoice, default_date_type, no_debit_before_maturity,
                group_lines, default_payment_mode, generate_move,
                offsetting_account, payment_order_ok, move_option,
                default_target_move, days_before_cancel, import_rule,
                sequence, payment_cancellable_on_qoqa, gift_card,
                payment_settlable_on_qoqa, refund_max_days
            ) VALUES (
                NEXTVAL('account_payment_mode_id_seq'), 1, 1,
                current_timestamp, current_timestamp, 'DTA USD', 3, 'fixed',
                'DTA', 23, 'outbound', True,
                CURRVAL('account_payment_method_id_seq'), False, 'due', False,
                True, 'same', True, 'bank_account', True, 'date', 'posted',
                30, 'always', 0, True, False, False, 0
            );

            INSERT INTO account_journal_outbound_payment_method_rel (
                journal_id, outbound_payment_method
            ) VALUES (23, CURRVAL('account_payment_method_id_seq'));

            UPDATE account_journal
            SET bank_account_id = 6
            WHERE id = 23;

            UPDATE account_invoice
            SET payment_mode_id = CURRVAL('account_payment_mode_id_seq')
            WHERE currency_id IN (
                SELECT id
                FROM res_currency
                WHERE name = 'USD'
            ) AND type = 'in_invoice';


            INSERT INTO account_payment_mode (
                id, create_uid, write_uid, create_date, write_date, name,
                company_id, bank_account_link, payment_method_code,
                fixed_journal_id, payment_type, active, payment_method_id,
                default_invoice, default_date_type, no_debit_before_maturity,
                group_lines, default_payment_mode, generate_move,
                offsetting_account, payment_order_ok, move_option,
                default_target_move, days_before_cancel, import_rule,
                sequence, payment_cancellable_on_qoqa, gift_card,
                payment_settlable_on_qoqa, refund_max_days
            ) VALUES (
                NEXTVAL('account_payment_mode_id_seq'), 1, 1,
                current_timestamp, current_timestamp, 'DTA EUR', 3, 'fixed',
                'DTA', 22, 'outbound', True,
                CURRVAL('account_payment_method_id_seq'), False, 'due', False,
                True, 'same', True, 'bank_account', True, 'date', 'posted',
                30, 'always', 0, True, False, False, 0
            );

            INSERT INTO account_journal_outbound_payment_method_rel (
                journal_id, outbound_payment_method
            ) VALUES (22, CURRVAL('account_payment_method_id_seq'));

            UPDATE account_journal
            SET bank_account_id = 5
            WHERE id = 22;

            UPDATE account_invoice
            SET payment_mode_id = CURRVAL('account_payment_mode_id_seq')
            WHERE currency_id IN (
                SELECT id
                FROM res_currency
                WHERE name = 'EUR'
            ) AND type = 'in_invoice';


            INSERT INTO account_payment_mode (
                id, create_uid, write_uid, create_date, write_date, name,
                company_id, bank_account_link, payment_method_code,
                fixed_journal_id, payment_type, active, payment_method_id,
                default_invoice, default_date_type, no_debit_before_maturity,
                group_lines, default_payment_mode, generate_move,
                offsetting_account, payment_order_ok, move_option,
                default_target_move, days_before_cancel, import_rule,
                sequence, payment_cancellable_on_qoqa, gift_card,
                payment_settlable_on_qoqa, refund_max_days
            ) VALUES (
                NEXTVAL('account_payment_mode_id_seq'), 1, 1,
                current_timestamp, current_timestamp, 'DTA CHF', 3, 'fixed',
                'DTA', 19, 'outbound', True,
                CURRVAL('account_payment_method_id_seq'), False, 'due', False,
                True, 'same', True, 'bank_account', True, 'date', 'posted',
                30, 'always', 0, True, False, False, 0
            );

            INSERT INTO account_journal_outbound_payment_method_rel (
                journal_id, outbound_payment_method
            ) VALUES (19, CURRVAL('account_payment_method_id_seq'));

            UPDATE account_journal
            SET bank_account_id = 2
            WHERE id = 19;

            UPDATE account_invoice
            SET payment_mode_id = CURRVAL('account_payment_mode_id_seq')
            WHERE currency_id NOT IN (
                SELECT id
                FROM res_currency
                WHERE name IN ('EUR', 'USD')
            ) AND type = 'in_invoice';


            INSERT INTO account_payment_mode (
                id, create_uid, write_uid, create_date, write_date, name,
                company_id, bank_account_link, payment_method_code,
                fixed_journal_id, payment_type, active, payment_method_id,
                default_invoice, default_date_type, no_debit_before_maturity,
                group_lines, default_payment_mode, generate_move,
                offsetting_account, payment_order_ok, move_option,
                default_target_move, days_before_cancel, import_rule,
                sequence, payment_cancellable_on_qoqa, gift_card,
                payment_settlable_on_qoqa, refund_max_days
            ) VALUES (
                NEXTVAL('account_payment_mode_id_seq'), 1, 1,
                current_timestamp, current_timestamp, 'DTA Salaires', 3,
                'fixed', 'DTA', 24, 'outbound', True,
                CURRVAL('account_payment_method_id_seq'), False, 'due', False,
                True, 'same', True, 'bank_account', True, 'date', 'posted',
                30, 'always', 0, True, False, False, 0
            );

            INSERT INTO account_journal_outbound_payment_method_rel (
                journal_id, outbound_payment_method
            ) VALUES (24, CURRVAL('account_payment_method_id_seq'));

            UPDATE account_journal
            SET bank_account_id = 7
            WHERE id = 24;


            INSERT INTO account_payment_mode (
                id, create_uid, write_uid, create_date, write_date, name,
                company_id, bank_account_link, payment_method_code,
                fixed_journal_id, payment_type, active, payment_method_id,
                default_invoice, default_date_type, no_debit_before_maturity,
                group_lines, default_payment_mode, generate_move,
                offsetting_account, payment_order_ok, move_option,
                default_target_move, days_before_cancel, import_rule,
                sequence, payment_cancellable_on_qoqa, gift_card,
                payment_settlable_on_qoqa, refund_max_days
            ) VALUES (
                NEXTVAL('account_payment_mode_id_seq'), 1, 1,
                current_timestamp, current_timestamp,
                'DTA CCP Pepsee 14-5058581', 3, 'fixed', 'DTA', 68,
                'outbound', True, CURRVAL('account_payment_method_id_seq'),
                False, 'due', False, True, 'same', True, 'bank_account', True,
                'date', 'posted', 30, 'always', 0, True, False, False, 0
            );

            INSERT INTO account_journal_outbound_payment_method_rel (
                journal_id, outbound_payment_method
            ) VALUES (68, CURRVAL('account_payment_method_id_seq'));

            UPDATE account_journal
            SET bank_account_id = 714
            WHERE id = 68;


            INSERT INTO account_payment_mode (
                id, create_uid, write_uid, create_date, write_date, name,
                company_id, bank_account_link, payment_method_code,
                fixed_journal_id, payment_type, active, payment_method_id,
                default_invoice, default_date_type, no_debit_before_maturity,
                group_lines, default_payment_mode, generate_move,
                offsetting_account, payment_order_ok, move_option,
                default_target_move, days_before_cancel, import_rule,
                sequence, payment_cancellable_on_qoqa, gift_card,
                payment_settlable_on_qoqa, refund_max_days
            ) VALUES (
                NEXTVAL('account_payment_mode_id_seq'), 1, 1,
                current_timestamp, current_timestamp, 'DTA Conférence QGroup',
                3, 'fixed', 'DTA', 65, 'outbound', True,
                CURRVAL('account_payment_method_id_seq'), False, 'due', False,
                True, 'same', True, 'bank_account', True, 'date', 'posted',
                30, 'always', 0, True, False, False, 0
            );

            INSERT INTO account_journal_outbound_payment_method_rel (
                journal_id, outbound_payment_method
            ) VALUES (65, CURRVAL('account_payment_method_id_seq'));

            UPDATE account_journal
            SET bank_account_id = 709
            WHERE id = 65;
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
            ctx.log_line('Could not create the qoqa_shipper_package_type with '
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
def correct_stock_location_complete_name(ctx):
    """ Correcting stock location complete name """
    ctx.env.cr.execute("""
        UPDATE stock_location l
        SET name = t.value
        FROM ir_translation t
        WHERE l.id = t.res_id
        AND l.name = 'stock.location,name'
        AND t.lang = 'fr_FR'
    """)
    location_model = ctx.env['stock.location'].with_context(lang='fr_FR')
    # few names not updated when we run it once,
    # don't want to lose time to search why
    # just run the update twice
    # all records will get the right name, bye
    for __ in range(2):
        locations = location_model.search([('location_id', '=', False)])
        for location in locations:
            # trigger complete_name function field, child records will recurse
            location.name = location.name


@anthem.log
def fix_wine_analysis_filters(ctx):
    """ Fixing wine move analysis filters """
    domain = [('model_id', '=', 'report.wine.move.analysis')]
    filters = ctx.env['ir.filters'].search(domain)
    for filter in filters:
        domain_replaces = [
            ("['attribute_set_id', '=', 2]", "['is_wine', '=', True]"),
            ("['attribute_set_id', '=', 3]", "['is_liquor', '=', True]"),
        ]
        new_domain = filter.domain
        for source, target in domain_replaces:
            new_domain = new_domain.replace(source, target)
        filter.domain = new_domain
        filter.context = '{}'


@anthem.log
def correct_parcel_tracking(ctx):
    """ Get tracking value from name, and add it in parcel_tracking"""
    ctx.env.cr.execute("""
        UPDATE stock_quant_package
        SET parcel_tracking = SPLIT_PART(name, ' - ', 2),
        name = SPLIT_PART(name, ' - ', 1)
        WHERE NAME ILIKE '% - %';
    """)


@anthem.log
def set_shop_domain(ctx):
    """ Setting up domains on shops """
    ctx.env.cr.execute("""
        UPDATE qoqa_shop
        SET domain = 'https://www.' || lower(name)
    """)


@anthem.log
def set_web_base_url(ctx):
    """ Configuring web.base.url """
    url = 'http://localhost:8069'
    ctx.env['ir.config_parameter'].set_param('web.base.url', url)
    ctx.env['ir.config_parameter'].set_param('web.base.url.freeze', 'True')


@anthem.log
def set_currency_exchange_journal(ctx):
    """ Configuring default currency exchange journal """
    ctx.env.cr.execute("""
        UPDATE res_company
        SET currency_exchange_journal_id = 62
        WHERE id = 3;
    """)


@anthem.log
def config_automatic_workflow(ctx):
    """ Configure automatic workflows """
    with ctx.log('Remove user_id from the sale automatic workflow filters'):
        ctx.env.cr.execute("""
            UPDATE ir_filters
            SET user_id = NULL
            WHERE id IN (SELECT res_id
                         FROM ir_model_data
                         WHERE model = 'ir.filters'
                         AND module LIKE 'sale_automatic_workflow%')
        """)
    with ctx.log('Disable validation of pickings'):
        ctx.env.cr.execute("""
            UPDATE sale_workflow_process SET validate_picking = false
        """)


@anthem.log
def cancel_fr_draft_invoices(ctx):
    """ Cancel french draft invoices """
    ctx.env.cr.execute("""
        UPDATE account_invoice
        SET state = 'cancel'
        WHERE company_id = 4 AND state = 'draft'
    """)


@anthem.log
def setup_cron(ctx):
    """ Setup the crons """
    ctx.env.cr.execute("""
        UPDATE ir_cron
        SET active = false
        WHERE id in (44, -- Automatic Workflow Job
                     33 -- Automatic Workflow Job FR
                     )
    """)


@anthem.log
def configure_account_type(ctx):
    """ Configure account types """
    ctx.env.cr.execute("""
        UPDATE account_account_type
        SET analytic_policy = 'always'
        WHERE id IN (
            SELECT res_id
            FROM ir_model_data
            WHERE name IN ('data_account_type_other_income',
                           'data_account_type_direct_costs',
                           'data_account_type_revenue')
            AND module = 'account'
        )
    """)


@anthem.log
def rename_qoqa_offer(ctx):
    """ Rename qoqa_offers (remove the qoqa_id, now in display_name)

    An offer named "[9487] Domo: Robot de Cuisine" becomes "Domo: Robot de
    Cuisine", the name_get/display_name will be prefixed with the qoqa_id
    """
    ctx.env.cr.execute("""
        UPDATE qoqa_offer
        SET name = substring(name FROM '\[\d+\] (.*)')
        WHERE name ~ '\[\d+\].*'
    """)
    ctx.env.cr.execute("""
        UPDATE qoqa_offer
        SET display_name = substring(display_name FROM '\[\d+\] (\[\d+\] .*)')
        WHERE display_name ~ '\[\d+\] \[\d+\].*'
    """)


@anthem.log
def delete_stock_translation(ctx):
    """ Remove new "Suppliers" translation (done in "specific_fct", but
        needed if "specific_fct" is updated at the same time than "stock")
    """
    ctx.env.cr.execute("""
        DELETE FROM ir_translation
        WHERE name = 'stock.location,name'
        AND lang IN ('de_DE', 'fr_FR')
        AND module = 'stock'
        AND src = 'Suppliers'
        AND value IN ('Vendeur', 'Lieferanten');
    """)


@anthem.log
def migrate_automatic_reconciliation(ctx):
    """
        Migrate from account.easy.reconcile to account.mass.reconcile
    """
    ctx.env.cr.execute("""
        DELETE FROM account_mass_reconcile_method;
        DELETE FROM account_mass_reconcile;
        INSERT INTO account_mass_reconcile (
            id, create_uid, create_date, write_uid, write_date,
            account, name, company_id, message_last_post)
        SELECT id, create_uid, create_date, write_uid, write_date,
               account, name, company_id, message_last_post
        FROM account_easy_reconcile;
        INSERT INTO account_mass_reconcile_method (
            id, create_uid, create_date, write_uid, write_date, name,
            task_id, date_base_on, account_profit_id, sequence, company_id,
            write_off, journal_id, filter, account_lost_id,
            expense_exchange_account_id, income_exchange_account_id
        ) SELECT id, create_uid, create_date, write_uid, write_date,
                 CASE WHEN name = 'easy.reconcile.advanced.bank_statement'
                      THEN 'mass.reconcile.advanced.ref'
                      ELSE OVERLAY(name PLACING 'mass.' FROM 1 FOR 5)
                 END, task_id,
                 CASE WHEN date_base_on = 'end_period_last_credit'
                      THEN 'actual'
                      ELSE 'newest'
                 END, account_profit_id, sequence, company_id, write_off,
                 journal_id, filter, account_lost_id,
                 expense_exchange_account_id, income_exchange_account_id
        FROM account_easy_reconcile_method;
    """)


@anthem.log
def disable_shipper_fee(ctx):
    """ Disabling former shipper fees """
    ctx.env.cr.execute("""
        UPDATE delivery_carrier
        SET active = false
        WHERE id IN (SELECT openerp_id FROM qoqa_shipper_fee)
    """)


@anthem.log
def move_stock_journal_to_picking_type(ctx):
    """ Move stock journal to picking types """
    picking_type_out = ctx.env.ref('stock.picking_type_out')
    sequence_out = picking_type_out.sequence_id
    picking_types = {}
    ctx.env.cr.execute("""
        SELECT id, name FROM stock_journal
    """)
    for id_, name in ctx.env.cr.fetchall():
        location_src = picking_type_out.default_location_src_id
        location_dest = picking_type_out.default_location_dest_id
        picking_types[id_] = create_or_update(
            ctx,
            'stock.picking.type',
            '__setup__.stock_picking_type_stock_journal_%s' % (id_,),
            {'name': name,
             'warehouse_id': picking_type_out.warehouse_id.id,
             'code': 'outgoing',
             'use_create_lots': picking_type_out.use_create_lots,
             'use_existing_lots': picking_type_out.use_existing_lots,
             'sequence_id': sequence_out.id,
             'default_location_src_id': location_src.id,
             'default_location_dest_id': location_dest.id,
             'sequence': picking_type_out.sequence + 1,
             'color': picking_type_out.color,
             }
        )
    for id_, picking_type in picking_types.iteritems():
        ctx.env.cr.execute("""
            SELECT count(*) FROM stock_picking
            WHERE stock_journal_id = %s
            AND picking_type_id = %s
        """, (id_, picking_type_out.id))
        picking_count, = ctx.env.cr.fetchone()
        msg = ('move %d pickings to picking type %s' %
               (picking_count, picking_type.name))
        with ctx.log(msg):
            ctx.env.cr.execute("""
                UPDATE stock_picking
                SET picking_type_id = %s
                WHERE stock_journal_id = %s
                AND picking_type_id = %s
            """, (picking_type.id, id_, picking_type_out.id))


@anthem.log
def main(ctx):
    """ Executing main entry point called after upgrade of addons """
    post_product.product_attribute_variants(ctx)
    post_product.product_brand(ctx)
    post_product.product_attributes(ctx)
    post_product.activate_variants(ctx)
    post_product.default_values(ctx)
    post_product.no_company(ctx)
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
    fix_wine_analysis_filters(ctx)
    correct_parcel_tracking(ctx)
    set_shop_domain(ctx)
    set_web_base_url(ctx)
    set_currency_exchange_journal(ctx)
    config_automatic_workflow(ctx)
    cancel_fr_draft_invoices(ctx)
    setup_cron(ctx)
    configure_account_type(ctx)
    rename_qoqa_offer(ctx)
    migrate_automatic_reconciliation(ctx)
    disable_shipper_fee(ctx)
    move_stock_journal_to_picking_type(ctx)
