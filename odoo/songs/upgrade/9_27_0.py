# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def fix_location_hierarchy(ctx):
    """ Set parent locations as 'view' and move current stock
        to 'Transit' name (run twice for specific cases) """
    location_obj = ctx.env['stock.location'].with_context(active_test=False)
    ctx.env.cr.execute("""
        SELECT id
        FROM stock_location
        WHERE usage = 'internal'
        AND id IN (
            SELECT DISTINCT location_id
            FROM stock_location
        );
    """)
    location_ids = [x[0] for x in ctx.env.cr.fetchall()]
    for location_id in location_ids:
        location = location_obj.browse(location_id)
        msg = ('Update location %s' % location.complete_name)
        with ctx.log(msg):
            new_location = location.copy({'usage': 'view', 'child_ids': []})
            # Move children to new location
            ctx.env.cr.execute("""
                UPDATE stock_location
                SET location_id = %s
                WHERE id IN %s
            """, (new_location.id, tuple(location.child_ids.ids)))
            ctx.env.cr.execute("""
                UPDATE stock_location
                SET location_id = %s,
                name = name || ' TRANSIT',
                complete_name = complete_name || ' TRANSIT'
                WHERE id = %s
            """, (new_location.id, location.id))
            ctx.env.cr.execute("""
                UPDATE ir_translation
                SET value = value || ' TRANSIT'
                WHERE name = 'stock.location,name'
                AND res_id = %s
            """, (location.id, ))


@anthem.log
def fix_inventory_quants(ctx):
    """ Create inventory to adjust negative quants """
    inventory_obj = ctx.env['stock.inventory'].with_context(active_test=False)
    quant_obj = ctx.env['stock.quant'].with_context(active_test=False)

    with ctx.log("Create inventory"):
        inventory = inventory_obj.create({
            'name': 'Correction niveau de stock post-migration',
            'location_id': ctx.env.ref('scenario.all_stock_location').id,
            'filter': 'partial',
            'company_id': ctx.env.ref('scenario.qoqa_ch').id
        })
        inventory.prepare_inventory()

    with ctx.log("Create inventory lines"):
        cr = ctx.env.cr
        cr.execute("""
            SELECT DISTINCT product_id
            FROM stock_quant
            WHERE qty < 0.0
            AND location_id IN (
                SELECT id
                FROM stock_location
                WHERE usage = 'internal'
            ) AND product_id NOT IN (
                SELECT DISTINCT product_id
                FROM stock_inventory_line
                WHERE inventory_id IN (
                    SELECT id
                    FROM stock_inventory
                    WHERE state = 'confirm'
                )
            ) ORDER BY product_id;
        """)
        product_ids = [x[0] for x in cr.fetchall()]
        for product_id in product_ids:
            cr.execute("""
                SELECT tmp2.location_id, tmp2.total
                FROM (
                    SELECT sum(qty) AS total,
                    stock_location.id as location_id FROM (
                        (
                            SELECT -sum(product_uom_qty) AS qty,
                            location_id
                            FROM stock_move
                            WHERE product_id = %(product_id)s
                            AND state = 'done'
                            GROUP BY location_id
                        ) UNION (
                            SELECT sum(product_uom_qty) AS qty,
                            location_dest_id AS location_id
                            FROM stock_move
                            WHERE product_id = %(product_id)s
                            AND state = 'done'
                            GROUP BY location_dest_id
                        )
                    ) tmp
                    LEFT JOIN stock_location
                    ON stock_location.id = tmp.location_id
                    WHERE stock_location.usage = 'internal'
                    GROUP BY stock_location.id
                ) tmp2""", {'product_id': product_id})
            for location_id, new_qty in cr.fetchall():
                try:
                    quants = quant_obj.search(
                        [('location_id', '=', location_id),
                         ('product_id', '=', product_id)]
                    )
                    old_qty = sum([x.qty for x in quants])
                    if old_qty != new_qty:
                        cr.execute("""
                            INSERT INTO stock_inventory_line
                            (inventory_id, product_id, product_uom_id,
                            location_id, theoretical_qty, product_qty,
                            company_id)
                            VALUES (%s, %s, 1, %s, %s, %s, 3)
                        """, (inventory.id, product_id, location_id,
                              old_qty, new_qty))
                except Exception:
                    continue

    with ctx.log("Prepare inventory for moves"):
        inventory.invalidate_cache()
        # Do action_done(), but avoid quantity check and process moves later
        inventory.action_check()
        inventory.write({'state': 'done'})


@anthem.log
def create_qoqa_logistic_partner(ctx):
    """ Create QoQa Services - Logistique partner for PO """
    Partner = ctx.env['res.partner']
    qoqa_logistic_partner = Partner.create({
        'name': 'QoQa Services SA - LOGISTIQUE',
        'street': "Rue de l'Industrie 66",
        'zip': '1030',
        'city': 'Bussigny',
        'phone': '+41 (0) 21 633 20 83'
    })
    ctx.env['ir.model.data'].create({
        'module': 'scenario',
        'name': 'qoqa_logistic_partner',
        'model': 'res.partner',
        'res_id': qoqa_logistic_partner.id
    })
    warehouse = ctx.env.ref('stock.warehouse0')
    warehouse.write({
        'partner_id': qoqa_logistic_partner.id
    })

@anthem.log
def main(ctx):
    fix_location_hierarchy(ctx)
    fix_inventory_quants(ctx)
    create_qoqa_logistic_partner(ctx)
