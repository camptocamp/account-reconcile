# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem

from ..common import column_exists, create_default_value


@anthem.log
def activate_variants(ctx):
    """ Activating variants """
    employee_group = ctx.env.ref('base.group_user')
    employee_group.write({
        'implied_ids': [(4, ctx.env.ref('product.group_product_variant').id)]
    })


@anthem.log
def product_attribute_variants(ctx):
    """ Migrating product attributes

    from the custom wizard to the odoo core variant attributes
    """
    cr = ctx.env.cr
    cr.execute("SELECT * FROM product_variant_dimension_type")
    for dimension_type in cr.dictfetchall():
        cr.execute(
            'SELECT id FROM product_attribute '
            'WHERE name = %s ',
            (dimension_type['name'],)
        )
        row = cr.fetchone()
        if row:
            attribute_id = row[0]
        else:
            cr.execute(
                'INSERT INTO product_attribute '
                '(name, create_date, write_date, create_uid, write_uid) '
                'VALUES (%s, %s, %s, %s, %s) '
                'RETURNING id',
                (dimension_type['name'],
                 dimension_type['create_date'],
                 dimension_type['write_date'],
                 dimension_type['create_uid'],
                 dimension_type['write_uid'])
            )
            attribute_id = cr.fetchone()[0]
        cr.execute('SELECT * from product_variant_dimension_option '
                   'WHERE type_id = %s', (dimension_type['id'],))
        for option in cr.dictfetchall():
                cr.execute(
                    'SELECT id FROM product_attribute_value '
                    'WHERE attribute_id = %s '
                    'AND name = %s ',
                    (attribute_id, option['name'])
                )
                if not cr.fetchone():
                    cr.execute(
                        'INSERT INTO product_attribute_value '
                        '(attribute_id, name, create_date, write_date, '
                        ' create_uid, write_uid) '
                        'VALUES (%s, %s, %s, %s, %s, %s) ',
                        (attribute_id,
                         option['name'],
                         option['create_date'],
                         option['write_date'],
                         option['create_uid'],
                         option['write_uid'])
                    )


@anthem.log
def product_brand(ctx):
    """ Migrating char field 'brand' to product_brand addon """
    # Do not fail if the fix has already been applied
    if column_exists(ctx, 'product_template', 'brand'):
        ctx.env.cr.execute("""
            INSERT INTO product_brand (name)
            SELECT distinct brand FROM product_template t
            WHERE NOT EXISTS (SELECT id FROM product_brand
                              WHERE name = t.brand)
            AND brand IS NOT NULL
        """)
        ctx.env.cr.execute("""
            UPDATE product_template
            SET product_brand_id = (SELECT id
                                    FROM product_brand
                                    WHERE name = product_template.brand)
            WHERE brand IS NOT NULL and product_brand_id IS NULL
        """)
        ctx.env.cr.execute("ALTER TABLE product_template DROP COLUMN brand")


@anthem.log
def product_attributes(ctx):
    """ Migrating product dynamic attributes to regular fields """
    ctx.env.cr.execute("""
        UPDATE product_template SET is_wine = True
        WHERE attribute_set_id = (
          SELECT id FROM attribute_set
          WHERE id = (
            SELECT res_id FROM ir_model_data
            WHERE model = 'attribute.set'
            AND name = 'set_wine'
          )
        )
    """)
    ctx.env.cr.execute("""
        UPDATE product_template SET is_liquor = True
        WHERE attribute_set_id = (
          SELECT id FROM attribute_set
          WHERE id = (
            SELECT res_id FROM ir_model_data
            WHERE model = 'attribute.set'
            AND name = 'set_liquor'
          )
        )
    """)
    ctx.env.cr.execute("""
        INSERT INTO wine_winemaker (name, create_date, write_date,
                                    create_uid, write_uid)
        SELECT TRIM(o.name),
               MIN(o.create_date),
               MIN(o.write_date),
               MIN(o.create_uid),
               MIN(o.write_uid)
          FROM product_template t
          INNER JOIN attribute_option o
          ON o.id = t.x_winemaker
          AND o.attribute_id = (
            SELECT id
            FROM attribute_attribute
            WHERE field_id = (
              SELECT id FROM ir_model_fields
              WHERE name = 'x_winemaker' AND model = 'product.template'
            )
          )
          WHERE t.x_winemaker IS NOT NULL
          AND NOT EXISTS (SELECT id
                          FROM wine_winemaker
                          WHERE name = TRIM(o.name))
          GROUP BY TRIM(o.name)
    """)
    ctx.env.cr.execute("""
        UPDATE product_template t
        SET winemaker_id = (
          SELECT w.id
          FROM wine_winemaker w
          INNER JOIN attribute_option o
          ON TRIM(o.name) = w.name
          INNER JOIN attribute_attribute a
          ON a.id = o.attribute_id
          INNER JOIN ir_model_fields f
          ON f.id = a.field_id
          AND f.name = 'x_winemaker' AND f.model = 'product.template'
          WHERE o.id = t.x_winemaker
        )
        WHERE x_winemaker IS NOT NULL AND winemaker_id IS NULL;
    """)
    ctx.env.cr.execute("""
        INSERT INTO wine_type (name, create_date, write_date,
                               create_uid, write_uid)
        SELECT TRIM(o.name),
               MIN(o.create_date),
               MIN(o.write_date),
               MIN(o.create_uid),
               MIN(o.write_uid)
          FROM product_template t
          INNER JOIN attribute_option o
          ON o.id = t.x_wine_type
          AND o.attribute_id = (
            SELECT id
            FROM attribute_attribute
            WHERE field_id = (
              SELECT id FROM ir_model_fields
              WHERE name = 'x_wine_type' AND model = 'product.template'
            )
          )
          WHERE t.x_wine_type IS NOT NULL
          AND NOT EXISTS (SELECT id FROM wine_type
                          WHERE name = TRIM(o.name))
          GROUP BY TRIM(o.name)
    """)
    ctx.env.cr.execute("""
        UPDATE product_template t
        SET wine_type_id = (
          SELECT w.id
          FROM wine_type w
          INNER JOIN attribute_option o
          ON TRIM(o.name) = w.name
          INNER JOIN attribute_attribute a
          ON a.id = o.attribute_id
          INNER JOIN ir_model_fields f
          ON f.id = a.field_id
          AND f.name = 'x_wine_type' AND f.model = 'product.template'
          WHERE o.id = t.x_wine_type
        )
        WHERE x_wine_type IS NOT NULL AND wine_type_id IS NULL
    """)
    ctx.env.cr.execute("""
        UPDATE product_template SET appellation = x_appellation
        WHERE x_appellation IS NOT NULL
    """)
    ctx.env.cr.execute("""
        UPDATE product_template SET millesime = x_millesime
        WHERE x_millesime IS NOT NULL
    """)
    ctx.env.cr.execute("""
        UPDATE product_template SET country_id = x_country_id
        WHERE x_country_id IS NOT NULL
    """)
    ctx.env.cr.execute("""
        UPDATE product_template SET ageing = x_ageing
        WHERE x_ageing IS NOT NULL
    """)
    ctx.env.cr.execute("""
        UPDATE product_template SET abv = x_abv
        WHERE x_abv IS NOT NULL
    """)
    ctx.env.cr.execute("""
        UPDATE product_template SET wine_short_name = x_wine_short_name
        WHERE x_wine_short_name IS NOT NULL
    """)
    ctx.env.cr.execute("""
        UPDATE product_template SET wine_region = x_wine_region
        WHERE x_wine_region IS NOT NULL
    """)


@anthem.log
def default_values(ctx):
    """ Update all product to be Control Purchase bill
    to be set on ordered quantity [MIGO-304]"""
    ctx.env.cr.execute("""
        UPDATE product_template set purchase_method='purchase'
    """)
    """ Setting default values on products """
    for company in ctx.env['res.company'].search([]):
        create_default_value(ctx,
                             'product.template',
                             'purchase_method',
                             company.id,
                             'purchase')
