# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

from openerp import tools
from openerp.osv import orm, fields


class report_wine_move_analysis(orm.Model):
    _name = "report.wine.move.analysis"
    _description = "Wine Moves Analysis"
    _auto = False
    _columns = {
        'date': fields.date('Date', readonly=True),
        'year': fields.char('Year', size=4, readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'month': fields.selection(
            [('01', 'January'),
             ('02', 'February'),
             ('03', 'March'),
             ('04', 'April'),
             ('05', 'May'),
             ('06', 'June'),
             ('07', 'July'),
             ('08', 'August'),
             ('09', 'September'),
             ('10', 'October'),
             ('11', 'November'),
             ('12', 'December')],
            string='Month',
            readonly=True),
        'partner_id': fields.many2one('res.partner',
                                      'Partner',
                                      readonly=True),
        'product_id': fields.many2one('product.product',
                                      'Product',
                                      readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'picking_id': fields.many2one('stock.picking',
                                      'Shipment',
                                      readonly=True),
        'type': fields.selection(
            [('out', 'Sending Goods'),
             ('in', 'Getting Goods'),
             ('internal', 'Internal'),
             ('other', 'Others')],
            string='Shipping Type',
            required=True,
            select=True,
            help="Shipping type specify, goods coming in or going out."),
        'location_id': fields.many2one(
            'stock.location',
            'Source Location',
            readonly=True,
            select=True,
            help="Sets a location if you produce at a fixed location. "
                 "This can be a partner location if you subcontract "
                 "the manufacturing operations."),
        'location_dest_id': fields.many2one(
            'stock.location',
            'Dest. Location',
            readonly=True,
            select=True,
            help="Location where the system will stock "
                 "the finished products."),
        'state': fields.selection(
            [('draft', 'Draft'),
             ('waiting', 'Waiting'),
             ('confirmed', 'Confirmed'),
             ('assigned', 'Available'),
             ('done', 'Done'),
             ('cancel', 'Cancelled')],
            string='Status',
            readonly=True,
            select=True),
        'product_qty': fields.integer('Quantity', readonly=True),
        'product_volume': fields.integer('Volume (Liters)', readonly=True),
        'categ_id': fields.many2one('product.category', 'Product Category'),
        'product_qty_in': fields.integer('In Qty', readonly=True),
        'product_qty_out': fields.integer('Out Qty', readonly=True),
        'product_volume_in': fields.integer('In Volume (Liters)', readonly=True),
        'product_volume_out': fields.integer('Out Volume (Liters)', readonly=True),
        'stock_journal': fields.many2one(
            'stock.journal',
            'Stock Journal',
            select=True),
        'attribute_set_id': fields.many2one(
            'attribute.set',
            'Attribute Set',
            select=True),
        'wine_bottle_id': fields.many2one(
            'wine.bottle',
            'Bottle',
            select=True),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_wine_move_analysis')
        cr.execute("""
            CREATE OR REPLACE view report_wine_move_analysis AS (
                SELECT
                        min(sm.id) as id,
                        date_trunc('day', sm.date) as date,
                        to_char(date_trunc('day',sm.date), 'YYYY') as year,
                        to_char(date_trunc('day',sm.date), 'MM') as month,
                        to_char(date_trunc('day',sm.date), 'YYYY-MM-DD') as day,
                        sm.location_id as location_id,
                        sm.picking_id as picking_id,
                        sm.company_id as company_id,
                        sm.location_dest_id as location_dest_id,
                        -- Beware: the total quantity and volume does not take the uom in account
                        -- That's the same thing in the "Stock Move Analysis" report
                        sum(sm.product_qty) as product_qty,
                        sum(sm.product_qty * wb.volume) as product_volume,
                        sum(
                            (CASE WHEN sp.type in ('out') THEN
                                     (sm.product_qty * pu.factor / pu2.factor)
                                  ELSE 0.0
                            END)
                        ) as product_qty_out,
                        sum(
                            (CASE WHEN sp.type in ('out') THEN
                                     (sm.product_qty * pu.factor / pu2.factor * COALESCE(wb.volume, 0))
                                  ELSE 0.0
                            END)
                        ) as product_volume_out,
                        sum(
                            (CASE WHEN sp.type in ('in') THEN
                                     (sm.product_qty * pu.factor / pu2.factor)
                                  ELSE 0.0
                            END)
                        ) as product_qty_in,
                        sum(
                            (CASE WHEN sp.type in ('in') THEN
                                     (sm.product_qty * pu.factor / pu2.factor * COALESCE(wb.volume, 0))
                                  ELSE 0.0
                            END)
                        ) as product_volume_in,
                        sm.partner_id as partner_id,
                        sm.product_id as product_id,
                        sm.state as state,
                        sm.product_uom as product_uom,
                        pt.categ_id as categ_id ,
                        coalesce(sp.type, 'other') as type,
                        sp.stock_journal_id AS stock_journal,
                        pt.attribute_set_id,
                        pt.wine_bottle_id
                    FROM
                        stock_move sm
                        LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                        INNER JOIN product_product pp ON (sm.product_id=pp.id)
                        LEFT JOIN product_uom pu ON (sm.product_uom=pu.id)
                          LEFT JOIN product_uom pu2 ON (sm.product_uom=pu2.id)
                        INNER JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                        INNER JOIN attribute_set ats ON (pt.attribute_set_id=ats.id)
                        LEFT JOIN wine_bottle wb ON (pt.wine_bottle_id=wb.id)
                    GROUP BY
                        coalesce(sp.type, 'other'),
                        date_trunc('day', sm.date),
                        sm.partner_id,
                        sm.state,
                        sm.product_uom,
                        sm.date_expected,
                        sm.product_id,
                        pt.standard_price,
                        sm.picking_id,
                        sm.company_id,
                        sm.location_id,
                        sm.location_dest_id,
                        pu.factor,
                        pt.categ_id,
                        sp.stock_journal_id,
                        year,
                        month,
                        day,
                        pt.attribute_set_id,
                        pt.wine_bottle_id
            )
        """)
