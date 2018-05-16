-- Add seller_price attribute to product_product
ALTER TABLE product_product ADD COLUMN seller_price double precision;

-- Set seller_price value using price attribute from templates supplierinfos if one and only one supplier is available.
WITH supplierinfo as (
    SELECT product_tmpl_id, price
    FROM product_supplierinfo
    WHERE product_id IS NULL
    GROUP BY product_tmpl_id, price
    HAVING COUNT(product_tmpl_id) = 1)
UPDATE product_product AS p SET seller_price = s.price FROM supplierinfo AS s WHERE p.product_tmpl_id = s.product_tmpl_id;
