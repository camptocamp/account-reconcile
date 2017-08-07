SELECT product_template_name AS "Nom de l'article",
       variants AS "Variante",
       shop AS "Shop",
       main_categ AS "Catégorie principale",
       second_categ AS "Catégorie secondaire",
       SUM(quantity) as "Quantity",
       COALESCE(SUM(price_unit_on_quant * quantity), 0) as "Valeur d'inventaire",
       COALESCE(SUM(price_unit_on_quant * quantity) / NULLIF(SUM(quantity), 0), 0) as "Prix moyen d'achat",
       MAX(max_date) AS "Dernière d'entrée de stock",
       current_location AS "Emplacement de stock"
FROM (
    SELECT product_product.default_code AS variants,
           product_template.name AS product_template_name,
           (CASE WHEN pc3.name IS NOT NULL THEN pc3.name ELSE (CASE WHEN pc2.name IS NOT NULL THEN pc2.name ELSE pc1.name END) END) AS shop,
           (CASE WHEN pc3.name IS NOT NULL AND pc2.name IS NOT NULL THEN pc2.name ELSE (CASE WHEN pc2.name IS NOT NULL THEN pc1.name ELSE null END) END) as main_categ,
           (CASE WHEN pc3.name IS NOT NULL AND pc2.name IS NOT NULL THEN pc1.name ELSE null END) AS second_categ,
           sum(quant.qty) AS quantity,
           quant.cost as price_unit_on_quant,
           MAX(bar.date at time zone 'GMT') max_date,
           dest_location.complete_name AS current_location
    FROM
        stock_quant as quant
    JOIN (
        SELECT DISTINCT ON (quant_id)
               quant_id,
               stock_move.date AS date,
               stock_location.id AS location_id
        FROM
            stock_quant_move_rel
        LEFT JOIN
            stock_move ON stock_move.id = stock_quant_move_rel.move_id
        LEFT JOIN
            stock_location ON stock_location.id = stock_move.location_dest_id
        WHERE stock_move.date <= '2017-06-30'
        AND stock_move.state = 'done'
        AND stock_location.active = 't'
        ORDER BY quant_id, stock_move.date DESC
    ) AS bar ON bar.quant_id = quant.id
    JOIN
        stock_location dest_location ON dest_location.id = bar.location_id
    JOIN
        product_product ON product_product.id = quant.product_id
    JOIN
        product_template ON product_template.id = product_product.product_tmpl_id
    LEFT JOIN
        product_category pc1 ON pc1.id = product_template.categ_id
    LEFT JOIN
        product_category pc2 ON pc2.id = pc1.parent_id
    LEFT JOIN
        product_category pc3 ON pc3.id = pc2.parent_id
    WHERE quant.qty > 0
    AND dest_location.usage IN ('internal', 'transit')
    AND dest_location.active = 't'
    AND dest_location.company_id = 3
    GROUP BY product_product.default_code, product_template_name, shop,
    main_categ, second_categ, price_unit_on_quant, current_location
) AS foo
GROUP BY variants, product_template_name, shop, main_categ, second_categ,
current_location;
