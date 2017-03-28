# -*coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import time

from pkg_resources import resource_stream

import anthem

from ..common import read_csv, req


@anthem.log
def migrate_qoqa_order_addresses(ctx):
    """ Migrating QoQa Order addresses

    Assuming we have a file containing columns

        id,shipping_address_id,billing_address_id

    For every qoqa order id we have to:
      1. find the odoo order
      2. if the shipping address has no flag qoqa_order_address:
        a. duplicate it, with active=False, qoqa_order_address=True
        b. create a binding with the new qoqa shipping_address_id
      3. repeat with the invoice address
      4. link the order with the new addresses

    """
    columns_to_copy = (
        "lang, company_id, create_uid, create_date, write_date, write_uid, "
        "comment, use_parent_address, street, supplier, city, "
        "user_id, zip, title, function, country_id, parent_id, employee, "
        "type, email, vat, website, fax, street2, phone, credit_limit, date, "
        "tz, customer, mobile, ref, birthdate, is_company, state_id, zip_id, "
        "notify_email, opt_out, display_name, vat_subjected, "
        "bank_statement_label, digicode, qoqa_address, "
        "commercial_partner_id, name, company_type")

    def copy_address(original_address_id, qoqa_address_id):
        ctx.env.cr.execute("""
        WITH addr_ins AS (
          INSERT INTO res_partner (%(fields)s, active, qoqa_order_address)
          SELECT %(fields)s, False, True FROM res_partner WHERE id = %%s
          RETURNING id AS address_id
        )
        INSERT INTO qoqa_address
        (create_uid, create_date, write_uid, write_date, sync_date,
         openerp_id, qoqa_id, backend_id)
         SELECT 1, NOW(), 1, NOW(), NOW(), address_id, %%s, 1
         FROM addr_ins
         RETURNING openerp_id
        """ % {'fields': columns_to_copy},
            (original_address_id, qoqa_address_id,))
        return ctx.env.cr.fetchone()[0]

    filepath = 'data/migration/order_address.csv'
    __, rows = read_csv(resource_stream(req, filepath))

    count = 0
    rows = list(rows)
    tstart = time.time()
    for qoqa_order_id, qoqa_shipping_id, qoqa_billing_id in rows:
        count += 1
        ctx.env.cr.execute("""
            SELECT o.id as order_id,
                   o.partner_invoice_id,
                   o.partner_shipping_id,
                   ainv.qoqa_order_address AS inv_done,
                   aship.qoqa_order_address AS ship_done,
                   qainv.id as inv_binding_id,
                   qaship.id as ship_binding_id
            FROM sale_order AS o
            INNER JOIN qoqa_sale_order qo
            ON qo.openerp_id = o.id
            INNER JOIN res_partner as ainv
            ON ainv.id = o.partner_invoice_id
            INNER JOIN res_partner as aship
            ON aship.id = o.partner_shipping_id
            LEFT OUTER JOIN qoqa_address qainv
            ON qainv.openerp_id = ainv.id
            LEFT OUTER JOIN qoqa_address qaship
            ON qaship.openerp_id = aship.id
            WHERE qo.qoqa_id = %s
        """, (qoqa_order_id,))
        row = ctx.env.cr.dictfetchone()
        if row:

            if not row['inv_binding_id']:
                # not a qoqa address, keep it
                new_invoice_id = None
            elif row['inv_done']:
                # already done in a previous migration
                new_invoice_id = None
            else:
                new_invoice_id = copy_address(row['partner_invoice_id'],
                                              qoqa_billing_id)

            if not row['ship_binding_id']:
                # not a qoqa address, keep it
                new_invoice_id = None
            elif row['ship_done']:
                # already done in a previous migration
                new_shipping_id = None
            else:
                new_shipping_id = copy_address(row['partner_shipping_id'],
                                               qoqa_shipping_id)

            order_id = row['order_id']
            if (new_invoice_id or new_shipping_id):
                ctx.env.cr.execute("""
                    UPDATE sale_order
                    SET partner_invoice_id = %s,
                        partner_shipping_id = %s
                    WHERE id = %s
                """, (new_invoice_id or row['partner_invoice_id'],
                      new_shipping_id or row['partner_shipping_id'],
                      order_id))

        if count % 1000 == 0:
            ctx.env.cr.commit()
            tdiff =  time.time() - tstart
            ctx.log_line('%d rows (%.2fs)...' % (count, tdiff))
            tstart = time.time()


@anthem.log
def main(ctx):
    migrate_qoqa_order_addresses(ctx)
