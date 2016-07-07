# -*- coding: utf-8 -*-
# Copyright 2011-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime

from openerp import _, api, exceptions, models

from openerp.addons.qoqa_product.models.wine import volume_to_string


class WineCHCSCVFormReport(models.AbstractModel):
    _name = 'report.wine_ch_report.report_wine_cscv_form'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(
            'wine_ch_report.report_wine_cscv_form')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        docargs.update(self.get_form_data(data))
        return report_obj.render('wine_ch_report.report_wine_cscv_form',
                                 docargs)

    def _get_wine_stocks(self, locs, beverage_type, inventory_date):
        """
        Returns a dict of stock per wine class and per type of wine
        - A dict:
             {Wine: <volume sum>}
        IMPORTANT: no negative stocks are used! This is to keep it consistent
        with the other Wine CH report, that only displays positive stocks.
        """
        is_wine = beverage_type == 'wine'
        is_liquor = beverage_type == 'liquor'
        cr = self.env.cr
        cr.execute("SELECT c.code, t.wine_type_id,"
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
                   "  WHERE t.is_wine = %s"
                   "    AND t.is_liquor = %s"
                   "  GROUP BY c.code, t.wine_type_id",
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
        return dict(((class_code, type_id), qty)
                    for class_code, type_id, qty in rows if qty)

    @api.model
    def get_form_data(self, data):
        """Populate a wine stock infos for qweb template"""

        # Reading form

        inventory_date = self._get_inventory_date(data)
        company_id = self._get_company_id(data)
        locations = self._get_locations(data)
        beverage_type = self._get_beverage_type(data)
        wine_stocks = self._get_wine_stocks(
            locations,
            beverage_type,
            inventory_date)

        if not wine_stocks:
            raise exceptions.UserError(_('No stock for given location'))

        wine_classes = self._get_wine_classes()
        wine_types = self._get_wine_types()

        exploitation_number = self._get_exploitation_number(company_id)

        return {
                'inventory_date': inventory_date,
                'exploitation_number': exploitation_number,
                'wine_classes': wine_classes,
                'wine_types': wine_types,
                'wine_stocks': wine_stocks,
                'format_volume': volume_to_string,
                }

    def _get_info(self, data, field):
        return data.get('form', {}).get(field)

    def _get_inventory_date(self, data):
        inventory_date = self._get_info(data, 'inventory_date')
        if not inventory_date:
            return str(datetime.today())
        return inventory_date

    def _get_company_id(self, data):
        return self._get_info(data, 'company_id')

    @api.model
    def _get_exploitation_number(self, company_id):
        company_obj = self.env['res.company']
        company = company_obj.browse(company_id)
        return company.wine_exploitation_number

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

    @api.model
    def _get_beverage_type(self, data):
        beverage_type = self._get_info(data, 'beverage_type')
        if not beverage_type:
            return 'wine'
        return beverage_type

    @api.model
    def _get_wine_classes(self):
        class_obj = self.env['wine.class']
        classes = class_obj.search([], order="code")
        return classes

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
