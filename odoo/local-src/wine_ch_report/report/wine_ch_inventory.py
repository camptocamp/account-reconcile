# -*- coding: utf-8 -*-
# Copyright 2011 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime

from openerp import api, models

from openerp.addons.qoqa_product.models.wine import volume_to_string


class WineCHInventoryReport(models.AbstractModel):
    _name = 'report.wine_ch_report.report_wine_inventory'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'wine_ch_report.report_wine_inventory')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        docargs.update(self.get_form_data(data))
        return report_obj.render('wine_ch_report.report_wine_inventory',
                                 docargs)

    @api.model
    def _get_sum_volume_by_wine(self, locs, beverage_type, inventory_date):
        """
        Returns a tuple of
        - A list of volumes ordered by size DESC
        - A dict:
          {<prod_id>:
            (<product_name,
             {<volume>: <qty>},
             <volume sum>)
             }
        """
        is_wine = beverage_type == 'wine'
        is_liquor = beverage_type == 'liquor'
        cr = self.env.cr
        cr.execute("SELECT p.id, t.name, wmk.name, b.volume,"
                   "       CASE "
                   "       WHEN q1.qty_in IS NULL THEN 0 "
                   "       ELSE q1.qty_in "
                   "       END - CASE "
                   "       WHEN q2.qty_out IS NULL THEN 0 "
                   "       ELSE q2.qty_out END AS qty,"
                   "       (CASE "
                   "        WHEN q1.qty_in IS NULL THEN 0 "
                   "        ELSE q1.qty_in "
                   "        END - CASE "
                   "        WHEN q2.qty_out IS NULL THEN 0 "
                   "        ELSE q2.qty_out "
                   "        END) * b.volume AS sum"
                   "  FROM product_product p "
                   "  INNER JOIN product_template t "
                   "  ON (p.product_tmpl_id=t.id) "
                   "  INNER JOIN wine_bottle b "
                   "  ON (b.id=t.wine_bottle_id) "
                   "  INNER JOIN wine_winemaker wmk "
                   "  ON (wmk.id=t.winemaker_id) "
                   "  LEFT OUTER JOIN "
                   "    (SELECT p.id, sum(m.product_qty) AS qty_in"
                   "      FROM stock_move m "
                   "      INNER JOIN product_product p "
                   "        ON (m.product_id=p.id) "
                   "      WHERE m.state = %s "
                   "        AND m.location_id NOT IN %s "
                   "        AND m.location_dest_id IN %s "
                   "        AND date(m.date) <= %s "
                   "      GROUP BY p.id) AS q1 "
                   "    ON q1.id = p.id "
                   "  LEFT OUTER JOIN "
                   "    (SELECT p.id, sum(m.product_qty) AS qty_out"
                   "      FROM stock_move m "
                   "      INNER JOIN product_product p "
                   "        ON (m.product_id=p.id) "
                   "      WHERE m.state = %s "
                   "        AND m.location_id IN %s "
                   "        AND m.location_dest_id NOT IN %s "
                   "        AND date(m.date) <= %s "
                   "      GROUP BY p.id) AS q2"
                   "    ON q2.id = p.id "
                   "  WHERE t.is_wine = %s"
                   "    AND t.is_liquor = %s",
                   ('done',
                    tuple(locs.ids),
                    tuple(locs.ids),
                    inventory_date,
                    'done',
                    tuple(locs.ids),
                    tuple(locs.ids),
                    inventory_date,
                    is_wine,
                    is_liquor
                    ))
        rows = cr.fetchall()
        volumes = set(
            vol for pid, pname, winemaker, vol, qty, sum_vol in rows if qty > 0
        )
        volumes = [v for v in sorted(list(volumes), reverse=True)]
        wine_lines = dict(
            (pid, (pname, winemaker, {vol: '%i' % qty}, sum_vol))
            for pid, pname, winemaker, vol, qty, sum_vol in rows if qty > 0
        )
        return volumes, wine_lines

    def _get_wine_ids(self, class_id, color):
        """
        Return a list of product ids for which wine_class_id is class_id
        The list must be ordered by size of bottle to ensure bigest bottles
        are listed first.  Also, return inactive products; if they have stock,
        they must still be displayed.
        """
        Product = self.env['product.product'].with_context(active_test=False)
        products = Product.search(
            [('wine_class_id', '=', class_id),
             ('wine_type_id', '=', color.id)],
        )
        products.sorted(lambda rec: rec.wine_bottle_id.volume,
                        reverse=True)
        return products.ids

    def get_form_data(self, data):
        """Populate a wine_report_lines attribute on each browse record
        that will be used by qweb template"""
        # Reading form

        inventory_date = self._get_inventory_date(data)
        locations = self._get_locations(data)
        beverage_type = self._get_beverage_type(data)
        wine_bottles, wine_lines = self._get_sum_volume_by_wine(
            locations, beverage_type, inventory_date)
        wine_classes = self._get_wine_classes(wine_lines.keys())
        wine_types = self._get_wine_types()

        return {
            'inventory_date': inventory_date,
            'wine_bottles': wine_bottles,
            'wine_classes': wine_classes,
            'wine_types': wine_types,
            'wine_lines': wine_lines,
            'get_wine_ids': self._get_wine_ids,
            'format_volume': volume_to_string,
            }

    def _get_info(self, data, field):
        return data.get('form', {}).get(field)

    def _get_inventory_date(self, data):
        inventory_date = self._get_info(data, 'inventory_date')
        if not inventory_date:
            return str(datetime.today())
        return inventory_date

    @api.model
    def _get_locations(self, data):
        location_ids = self._get_info(data, 'location_ids')
        if not location_ids or len(location_ids) == 0:
            return self._get_all('stock.location')
        else:
            # Retrieve children locations
            locations = self._get_all_children(
                location_ids, 'stock.location')
        return locations

    def _get_beverage_type(self, data):
        beverage_type = self._get_info(data, 'beverage_type')
        if not beverage_type:
            return 'wine'
        return beverage_type

    @api.model
    def _get_wine_classes(self, product_ids):
        class_obj = self.env['wine.class']
        product_obj = self.env['product.product']
        # find classes with wines in stock
        products = product_obj.browse(product_ids)
        leaf_classes = products.mapped('wine_class_id')

        # get parents of those leaves
        ancestors = self.env['wine.class']
        for leaf in leaf_classes:
            ancestors |= class_obj.search(
                [('parent_left', '<', leaf.parent_left),
                 ('parent_left', '<', leaf.parent_right),
                 ('parent_right', '>', leaf.parent_left),
                 ('parent_right', '>', leaf.parent_right),
                 ])
        return (ancestors | leaf_classes).sorted(lambda rec: rec.code)

    @api.model
    def _get_wine_types(self):
        return self.env['wine.type'].search([])

    @api.model
    def _get_all(self, model):
        model_obj = self.env[model]
        return model_obj.search([])

    @api.model
    def _get_all_children(self, ids, model):
        model_obj = self.env[model]
        return model_obj.search([('id', 'child_of', ids)])
