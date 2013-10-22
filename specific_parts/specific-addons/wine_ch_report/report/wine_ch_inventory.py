# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
#    Copyright Camptocamp SA 2011
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime

from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _

from openerp.addons.wine_ch_report.wine_bottle import volume_to_string


class WineCHInventoryWebkit(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(WineCHInventoryWebkit, self).__init__(cr, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'report_name': _('Wine CH Inventory'),
            })

    def _get_sum_volume_by_wine(self, loc_ids, set_id):
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
        cr = self.cursor
        cr.execute("SELECT p.id, t.name, b.volume,"
                   "       CASE WHEN q1.qty_in IS NULL THEN 0 ELSE q1.qty_in END - CASE WHEN q2.qty_out IS NULL THEN 0 ELSE q2.qty_out END AS qty,"
                   "       (CASE WHEN q1.qty_in IS NULL THEN 0 ELSE q1.qty_in END - CASE WHEN q2.qty_out IS NULL THEN 0 ELSE q2.qty_out END) * b.volume AS sum"
                   "  FROM product_product p "
                   "  INNER JOIN product_template t ON (p.product_tmpl_id=t.id) "
                   "  INNER JOIN wine_bottle b ON (b.id=t.wine_bottle_id) "
                   "  LEFT OUTER JOIN "
                   "    (SELECT p.id, sum(m.product_qty) AS qty_in"
                   "      FROM stock_move m "
                   "      INNER JOIN product_product p "
                   "        ON (m.product_id=p.id) "
                   "      WHERE m.state IN %s "
                   "        AND m.location_id NOT IN %s "
                   "        AND m.location_dest_id IN %s "
                   "      GROUP BY p.id) AS q1 "
                   "    ON q1.id = p.id "
                   "  LEFT OUTER JOIN "
                   "    (SELECT p.id, sum(m.product_qty) AS qty_out"
                   "      FROM stock_move m "
                   "      INNER JOIN product_product p "
                   "        ON (m.product_id=p.id) "
                   "      WHERE m.state IN %s "
                   "        AND m.location_id IN %s "
                   "        AND m.location_dest_id NOT IN %s "
                   "      GROUP BY p.id) AS q2"
                   "    ON q2.id = p.id "
                   "  WHERE t.attribute_set_id = %s",
                   (('confirmed', 'assigned', 'waiting', 'done'),
                    tuple(loc_ids),
                    tuple(loc_ids),
                    ('confirmed', 'assigned', 'waiting', 'done'),
                    tuple(loc_ids),
                    tuple(loc_ids),
                    set_id,
                    ))
        rows = cr.fetchall()
        volumes = set(vol for pid, pname, vol, qty, sum_vol in rows)
        volumes = [v for v in sorted(list(volumes), reverse=True)]
        wine_lines = dict((pid, (pname, {vol: '%i' % qty}, sum_vol))
                          for pid, pname, vol, qty, sum_vol in rows)
        return volumes, wine_lines


    def _get_wine_ids(self, class_id, color):
        """
        Return a list of product ids for which wine_class_id is class_id
        The list must be ordered by size of bottle to ensure bigest bottles
        are listed first
        """
        product_obj = self.pool.get('product.product')
        product_ids = product_obj.search(self.cr, self.uid,
                [('wine_class_id', '=', class_id),
                 ('x_wine_type', '=', color)]
                )
        products = product_obj.browse(self.cr, self.uid, product_ids)
        products.sort(key=lambda prod: prod.wine_bottle_id.volume, reverse=True)
        return [p.id for p in products]

    def set_context(self, objects, data, ids, report_type=None):
        """Populate a wine_report_lines attribute on each browse record that will be used
        by mako template"""

        # Reading form

        inventory_date = self._get_inventory_date(data)
        location_ids = self._get_location_ids(data)
        attribute_set_id = self._get_attribute_set_id(data)
        wine_bottles, wine_lines = self._get_sum_volume_by_wine(location_ids, attribute_set_id)
        wine_classes = self._get_wine_classes(wine_lines.keys())
        wine_types = self._get_wine_types()

        self.localcontext.update({
            'inventory_date': inventory_date,
            'wine_bottles': wine_bottles,
            'wine_classes': wine_classes,
            'wine_types': wine_types,
            'wine_lines': wine_lines,
            'get_wine_ids': self._get_wine_ids,
            'format_volume': volume_to_string,
            })
        return super(WineCHInventoryWebkit, self).set_context(objects, data, ids,
                                                           report_type=report_type)

    def _get_info(self, data, field):
        return data.get('form', {}).get(field)

    def _get_inventory_date(self, data):
        inventory_date = self._get_info(data, 'inventory_date')
        if not inventory_date:
            return str(datetime.today())
        return inventory_date

    def _get_location_ids(self, data):
        location_ids = self._get_info(data, 'location_ids')
        if not location_ids:
            return self._get_all_ids('stock.location')
        return location_ids

    def _get_attribute_set_id(self, data):
        set_id = self._get_info(data, 'attribute_set_id')
        if not set_id:
            set_ids = self._search_wine_set_id()
            return set_ids and set_ids[0]
        return set_id[0]

    def _get_wine_classes(self, product_ids):
        class_obj = self.pool.get('wine.class')
        product_obj = self.pool.get('product.product')
        # have an ordered list of ids
        class_ids = class_obj.search(self.cr, self.uid,
                                     [], order="code")
        # find classes with wines in stock
        products = product_obj.browse(self.cr, self.uid, product_ids)
        leaf_classes = set([p.wine_class_id for p in products])
        leaf_ids = [l.id for l in leaf_classes]

        # get parents of those leaves
        ancestor_ids = []
        for leaf in leaf_classes:
            ancestor_ids += class_obj.search(self.cr, self.uid,
                    [('parent_left', '<', leaf.parent_left),
                     ('parent_left', '<', leaf.parent_right),
                     ('parent_right', '>', leaf.parent_left),
                     ('parent_right', '>', leaf.parent_right),
                     ])

        class_ids = [c for c in class_ids if c in ancestor_ids + leaf_ids]
        return class_obj.browse(self.cr, self.uid, class_ids)

    def _get_wine_types(self):
        option_obj = self.pool.get('attribute.option')
        option_ids = option_obj.search(self.cr, self.uid, [('attribute_id.name', '=', 'x_wine_type')])
        return option_obj.browse(self.cr, self.uid, option_ids)

    def _search_wine_set_id(self):
        """
        Search for the wine attribute set
        """
        model_obj = self.pool.get('attribute.set')
        return model_obj.search(self.cr, self.uid,
                                ['|',
                                 ('name', 'ilike', 'wine'),
                                 ('name', 'ilike', 'vin'),
                                 ])

    def _get_all_ids(self, model):
        model_obj = self.pool.get(model)
        return model_obj.search(self.cr, self.uid, [])


report_sxw.report_sxw('report.wine.ch.inventory.webkit',
                      'product.product',
                      'addons/wine_ch_report/report/templates/wine_ch_inventory.mako.html',
                      parser=WineCHInventoryWebkit)
