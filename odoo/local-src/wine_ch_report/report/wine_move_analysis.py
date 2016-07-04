# -*- coding: utf-8 -*-
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp import tools
from openerp import models, fields


class ReportWineMoveAnalysis(models.Model):
    _name = "report.wine.move.analysis"
    _description = "Wine Moves Analysis"
    _auto = False
    date = fields.Datetime('Date', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    picking_id = fields.Many2one('stock.picking', 'Shipment', readonly=True)
    stock_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Shipping Type',
        required=True,
        index=True,
        help="Shipping type specify, goods coming in or going out.")
    location_id = fields.Many2one(
        'stock.location',
        'Source Location',
        readonly=True,
        index=True,
        help="Sets a location if you produce at a fixed location. "
             "This can be a partner location if you subcontract "
             "the manufacturing operations.")
    location_dest_id = fields.Many2one(
        'stock.location',
        'Dest. Location',
        readonly=True,
        index=True,
        help="Location where the system will stock "
             "the finished products.")
    state = fields.Selection(
        [('draft', 'Draft'),
         ('waiting', 'Waiting'),
         ('confirmed', 'Confirmed'),
         ('assigned', 'Available'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')],
        string='Status',
        readonly=True,
        index=True)
    product_qty = fields.Integer('Quantity', readonly=True)
    product_volume = fields.Integer('Volume (Liters)', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category')
    product_qty_in = fields.Integer('In Qty', readonly=True)
    product_qty_out = fields.Integer('Out Qty', readonly=True)
    product_volume_in = fields.Float('In Volume (Liters)', readonly=True)
    product_volume_out = fields.Float('Out Volume (Liters)', readonly=True)
    is_wine = fields.Boolean('Is wine')
    is_liquor = fields.Boolean('Is Liquor')
    wine_bottle_id = fields.Many2one(
        'wine.bottle',
        'Bottle',
        index=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_wine_move_analysis')
        cr.execute("""
        CREATE OR REPLACE view report_wine_move_analysis AS (
            SELECT
                    min(sm.id) as id,
                    date_trunc('day', sm.date) as date,
                    sm.location_id as location_id,
                    sm.picking_id as picking_id,
                    spt.id as stock_picking_type_id,
                    sm.company_id as company_id,
                    sm.location_dest_id as location_dest_id,
                    -- Beware: the total quantity and volume does not
                    -- take the uom in account
                    -- That's the same thing in the
                    -- "Stock Move Analysis" report
                    sum(sm.product_qty) as product_qty,
                    sum(sm.product_qty * wb.volume) as product_volume,
                    sum(
                        (CASE WHEN spt.code in ('outgoing') THEN
                                    (sm.product_qty * pu.factor / pu2.factor)
                                ELSE 0.0
                        END)
                    ) as product_qty_out,
                    sum(
                        (CASE WHEN spt.code in ('outgoing') THEN
                                    (sm.product_qty * pu.factor /
                                     pu2.factor * COALESCE(wb.volume, 0))
                                ELSE 0.0
                        END)
                    ) as product_volume_out,
                    sum(
                        (CASE WHEN spt.code in ('incoming') THEN
                                    (sm.product_qty * pu.factor / pu2.factor)
                                ELSE 0.0
                        END)
                    ) as product_qty_in,
                    sum(
                        (CASE WHEN spt.code in ('incoming') THEN
                                    (sm.product_qty * pu.factor /
                                     pu2.factor * COALESCE(wb.volume, 0))
                                ELSE 0.0
                        END)
                    ) as product_volume_in,
                    sm.partner_id as partner_id,
                    sm.product_id as product_id,
                    sm.state as state,
                    sm.product_uom as product_uom,
                    pt.categ_id as categ_id ,
                    sp.picking_type_id as picking_type_id,
                    pt.is_wine,
                    pt.is_liquor,
                    pt.wine_bottle_id
                FROM
                    stock_move sm
                    LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                    INNER JOIN stock_picking_type spt
                      ON (sp.picking_type_id=spt.id)
                    INNER JOIN product_product pp ON (sm.product_id=pp.id)
                    LEFT JOIN product_uom pu ON (sm.product_uom=pu.id)
                    LEFT JOIN product_uom pu2 ON (sm.product_uom=pu2.id)
                    INNER JOIN product_template pt
                      ON (pp.product_tmpl_id=pt.id)
                    LEFT JOIN wine_bottle wb ON (pt.wine_bottle_id=wb.id)
                WHERE
                    pt.is_wine = TRUE
                    OR pt.is_liquor = TRUE
                GROUP BY
                    sp.picking_type_id,
                    date_trunc('day', sm.date),
                    sm.partner_id,
                    sm.state,
                    sm.product_uom,
                    sm.date_expected,
                    sm.product_id,
                    sm.picking_id,
                    spt.id,
                    sm.company_id,
                    sm.location_id,
                    sm.location_dest_id,
                    pu.factor,
                    pt.categ_id,
                    pt.is_wine,
                    pt.is_liquor,
                    pt.wine_bottle_id
        )
        """)
