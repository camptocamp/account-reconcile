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
from openerp.osv import orm
from openerp.tools.translate import _

from openerp.addons.wine_ch_report.wine_bottle import volume_to_string


class WineCHCSCVFormWebkit(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(WineCHCSCVFormWebkit, self).__init__(cr, uid, name,
                                                   context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'report_name': _('Wine CH Inventory'),
            })

    def _get_wine_stocks(self, loc_ids, set_id, inventory_date):
        """
        Returns a dict of stock per wine class and per type of wine
        - A dict:
             {Wine: <volume sum>}
        IMPORTANT: no negative stocks are used! This is to keep it consistent
        with the other Wine CH report, that only displays positive stocks.
        """
        cr = self.cursor
        # TODO: x_wine_type is now wine_type_id
        cr.execute("SELECT c.code, t.x_wine_type,"
                   "       SUM(GREATEST((CASE WHEN q1.qty_in IS NULL THEN 0 "
                   "            ELSE q1.qty_in END"
                   "        - CASE WHEN q2.qty_out IS NULL THEN 0 "
                   "          ELSE q2.qty_out END), 0)"
                   "        * b.volume) AS sum"
                   "  FROM product_product p "
                   "  INNER JOIN product_template t "
                   "  ON (p.product_tmpl_id=t.id) "
                   "  INNER JOIN wine_bottle b ON (b.id=t.wine_bottle_id) "
                   "  INNER JOIN wine_class c ON (c.id=t.wine_class_id) "
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
                   "  WHERE t.attribute_set_id = %s"
                   "  GROUP BY c.code, t.x_wine_type",
                   ('done',
                    tuple(loc_ids),
                    tuple(loc_ids),
                    inventory_date,
                    'done',
                    tuple(loc_ids),
                    tuple(loc_ids),
                    inventory_date,
                    set_id,
                    ))
        rows = cr.fetchall()
        return dict(((class_code, type_id), qty)
                    for class_code, type_id, qty in rows if qty)

    def set_context(self, objects, data, ids, report_type=None):
        """Populate a wine stock infos for mako template"""

        # Reading form

        inventory_date = self._get_inventory_date(data)
        company_id = self._get_company_id(data)
        location_ids = self._get_location_ids(data)
        attribute_set_id = self._get_attribute_set_id(data)
        wine_stocks = self._get_wine_stocks(location_ids,
                                            attribute_set_id,
                                            inventory_date)

        if not wine_stocks:
            raise orm.except_orm('Error', 'No stock for given location')

        wine_classes = self._get_wine_classes()
        wine_types = self._get_wine_types()

        exploitation_number = self._get_exploitation_number(company_id)

        self.localcontext.update({
            'inventory_date': inventory_date,
            'exploitation_number': exploitation_number,
            'wine_classes': wine_classes,
            'wine_types': wine_types,
            'wine_stocks': wine_stocks,
            'format_volume': volume_to_string,
            })
        return super(WineCHCSCVFormWebkit,
                     self).set_context(objects, data, ids,
                                       report_type=report_type)

    def _get_info(self, data, field):
        return data.get('form', {}).get(field)

    def _get_inventory_date(self, data):
        inventory_date = self._get_info(data, 'inventory_date')
        if not inventory_date:
            return str(datetime.today())
        return inventory_date

    def _get_company_id(self, data):
        return self._get_info(data, 'company_id')

    def _get_exploitation_number(self, company_id):
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(self.cr, self.uid, company_id)
        return company.wine_exploitation_number

    def _get_location_ids(self, data):
        location_ids = self._get_info(data, 'location_ids')
        if not location_ids or len(location_ids) == 0:
            return self._get_all_ids('stock.location')
        else:
            # Retrieve children locations
            location_ids = self._get_all_children(
                location_ids, 'stock.location')
        return location_ids

    def _get_attribute_set_id(self, data):
        set_id = self._get_info(data, 'attribute_set_id')
        if not set_id:
            set_ids = self._search_wine_set_id()
            return set_ids and set_ids[0]
        return set_id[0]

    def _get_wine_classes(self):
        class_obj = self.pool.get('wine.class')
        class_ids = class_obj.search(self.cr, self.uid,
                                     [], order="code")
        return class_obj.browse(self.cr, self.uid, class_ids)

    def _get_wine_types(self):
        # TODO: model types are now stored in wine_type
        option_obj = self.pool.get('attribute.option')
        option_ids = option_obj.search(
            self.cr, self.uid,
            [('attribute_id.name', '=', 'x_wine_type')])
        return option_obj.browse(self.cr, self.uid, option_ids)

    def _search_wine_set_id(self):
        """
        Search for the wine attribute set
        """
        # TODO: replace by a domain on product_template.is_wine
        model_obj = self.pool.get('attribute.set')
        return model_obj.search(self.cr, self.uid,
                                ['|',
                                 ('name', 'ilike', 'wine'),
                                 ('name', 'ilike', 'vin'),
                                 ])

    def _get_all_ids(self, model):
        model_obj = self.pool.get(model)
        return model_obj.search(self.cr, self.uid, [])

    def _get_all_children(self, ids, model):
        model_obj = self.pool.get(model)
        return model_obj.search(self.cr, self.uid, [('id', 'child_of', ids)])


report_sxw.report_sxw(
    'report.wine.ch.cscv_form.webkit',
    'wine.ch.inventory.wizard',
    'addons/wine_ch_report/report/templates/wine_ch_cscv_form.mako.html',
    parser=WineCHCSCVFormWebkit)
