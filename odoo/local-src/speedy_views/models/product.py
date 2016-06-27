# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from openerp import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _sales_count(self):
        # the original method uses the 'sale_report' view
        # and is awfully slow
        query = ("SELECT l.product_id, "
                 "       SUM(l.product_uom_qty / u.factor * u2.factor) "
                 "FROM sale_order_line l "
                 "INNER JOIN sale_order o "
                 "ON o.id = l.order_id "
                 "INNER JOIN product_product p "
                 "ON p.id = l.product_id "
                 "LEFT JOIN product_template t "
                 "ON p.product_tmpl_id = t.id "
                 "LEFT JOIN product_uom u "
                 "ON u.id = l.product_uom "
                 "LEFT JOIN product_uom u2 "
                 "ON u2.id = t.uom_id "
                 "WHERE o.state IN %s "
                 "AND l.product_id IN %s "
                 "GROUP BY l.product_id")
        self.env.cr.execute(query, (('sale', 'done'), tuple(self.ids)))
        sales_counts = dict(self.env.cr.fetchall())
        for product in self:
            product.sales_count = sales_counts.get(product.id, 0)
        return sales_counts

    @api.multi
    def _purchase_count(self):
        # the original method uses the 'purchase_report' view
        # and is awfully slow
        query = ("SELECT l.product_id, "
                 "       SUM(l.product_qty / u.factor * u2.factor) "
                 "FROM purchase_order_line l "
                 "INNER JOIN purchase_order o "
                 "ON o.id = l.order_id "
                 "INNER JOIN product_product p "
                 "ON p.id = l.product_id "
                 "LEFT JOIN product_template t "
                 "ON p.product_tmpl_id = t.id "
                 "LEFT JOIN product_uom u "
                 "ON u.id = l.product_uom "
                 "LEFT JOIN product_uom u2 "
                 "ON u2.id = t.uom_id "
                 "WHERE o.state IN %s "
                 "AND l.product_id IN %s "
                 "GROUP BY l.product_id")
        self.env.cr.execute(query, (('purchase', 'done'), tuple(self.ids)))
        purchase_counts = dict(self.env.cr.fetchall())
        for product in self:
            product.purchase_count = purchase_counts.get(product.id, 0)
        return purchase_counts
