DELETE FROM ir_translation
WHERE name = 'stock.location,name'
AND lang IN ('de_DE', 'fr_FR')
AND module = 'stock'
AND src = 'Suppliers'
AND value IN ('Vendeur', 'Lieferanten');