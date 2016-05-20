# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from __future__ import division
from datetime import timedelta
import pytz
from openerp import models, fields, api, exceptions, _


# TODO: see what should be removed
# now offers will be imported, not created from Odoo
class QoqaOffer(models.Model):
    _name = 'qoqa.offer'
    _description = 'QoQa Offer'
    _inherit = ['mail.thread']

    _order = 'date_begin, time_begin'

    ref = fields.Char(string='Offer Reference', readonly=True, index=True)
    name = fields.Char(
        string='Ref and Name',
        readonly=True,
    )
    main_brand = fields.Char(
        string='Main Brand',
        readonly=True,
    )
    main_product_name = fields.Char(
        string='Main Product Name',
        readonly=True,
    )
    title = fields.Char(
        string='Title',
        readonly=True,
        translate=True,
    )
    description = fields.Html(
        string='Description',
        readonly=True,
        translate=True,
    )
    note = fields.Html(string='Internal Notes')
    qoqa_shop_id = fields.Many2one(
        comodel_name='qoqa.shop',
        string='Sell on',
        readonly=True,
    )
    shop_kanban_image = fields.Binary(
        related='qoqa_shop_id.kanban_image',
        string='Company',
        readonly=True,
        store=True,
    )
    position_ids = fields.One2many(
        comodel_name='qoqa.offer.position',
        inverse_name='offer_id',
        string='Positions',
    )
    # date & time are split in 2 fields
    # because they should not be based on the UTC
    # if one says that a offer start on 2013-10-07 at 00:00
    # the QoQa backend expect to receive this date and time
    # without consideration of the UTC time
    date_begin = fields.Date(
        string='Start Date',
        readonly=True,
        index=True,
    )
    time_begin = fields.Float(
        string='Start Time',
        readonly=True,
        index=True,
    )
    date_end = fields.Date(
        string='End Date',
        readonly=True,
    )
    time_end = fields.Float(
        string='End Time',
        readonly=True,
    )
    # for the display on the tree and kanban views
    datetime_begin = fields.Char(
        compute='_compute_full_dates',
        string='Begins at',
        store=True,
    )
    datetime_end = fields.Char(
        compute='_compute_full_dates',
        string='Ends at',
        store=True,
    )
    # used in search view 'current' filter
    # a datetime is necessary instead of a char
    datetime_begin_filter = fields.Datetime(
        compute='_compute_full_dates',
        string='Begins at',
        store=True,
    )
    datetime_end_filter = fields.Datetime(
        compute='_compute_full_dates',
        string='Ends at',
        store=True,
    )
    # display on the calendar
    # use a date and not a datetime to avoid timezone shifts
    date_begin_calendar = fields.Date(
        compute='_compute_full_dates',
        string='Begins at (Calendar)',
        store=True,
    )
    date_end_calendar = fields.Date(
        compute='_compute_full_dates',
        string='Ends at (Calendar)',
        store=True,
        help="When an ending date is date_begin + 1 day at 00:00 "
             "this date is set at date_begin, so the calendar won't "
             "display the offer on 2 days",
    )
    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Delivery Method',
        domain="[('qoqa_type', '=', 'service')]",
        readonly=True,
    )
    shipper_rate_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Shipper Rate',
        readonly=True,
        domain="[('qoqa_type', '=', 'rate')]",
    )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        domain="[('type', '=', 'sale')]",
        readonly=True,
    )
    lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Language',
        readonly=True,
        domain=[('translatable', '=', True)],
    )
    company_id = fields.Many2one(
        related='qoqa_shop_id.company_id',
        string='Company',
        readonly=True,
        store=True,
    )
    date_warranty = fields.Date(
        string='Warranty Expiration',
        readonly=True,
    )
    send_newsletters = fields.Boolean(
        string='Send newsletters',
        readonly=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        readonly=True,
    )
    sale_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='offer_id',
        string='Sales Orders',
        readonly=True,
    )
    # # related to main position for kanban view:
    currency_symbol = fields.Char(
        related='pricelist_id.currency_id.symbol',
        string='Currency',
        readonly=True,
    )
    main_lot_price = fields.Float(
        string='Unit Price',
        readonly=True,
    )
    main_regular_price = fields.Float(
        string='Unit Price',
        readonly=True,
    )

    @api.depends('date_begin', 'time_begin', 'date_end', 'time_end')
    def compute_full_dates(self):
        """ Convert the dates for the display on the different views.

        Do not use the normal datetime fields to avoid timezone shifts.

        """
        lang = self.env['res.lang'].search([('code', '=', 'fr_FR')])

        dfmt = '%Y-%m-%d'
        tfmt = '%H:%M:%S'
        if lang:
            if lang.date_format:
                dfmt = lang.date_format
            if lang.time_format:
                tfmt = lang.time_format
        fmt = dfmt + ' ' + tfmt
        for offer in self:
            begin = fields.Date.from_string(offer.date_begin)
            begin += timedelta(hours=offer.time_begin)
            end = fields.Date.from_string(offer.date_end)
            end += timedelta(hours=offer.time_end)

            # For filters we need a utc time, qoqa datetimes are in the
            # following tz:
            local = pytz.timezone('Europe/Zurich')
            begin_local = local.localize(begin, is_dst=None)
            begin_utc = begin_local.astimezone(pytz.utc)
            end_local = local.localize(end, is_dst=None)
            end_utc = end_local.astimezone(pytz.utc)

            # Avoid to display an offer on number of calendar days + 1
            # when the last day is at midnight. Example:
            # Begin: 2013-12-04 00:00 End: 2013-12-05 00:00
            # We consider the last day to be 2013-12-04
            if offer.time_end == 0:
                calendar_end = end - timedelta(days=1)
            else:
                calendar_end = end

            offer.datetime_begin = begin.strftime(fmt)
            offer.datetime_end = end.strftime(fmt)
            offer.datetime_begin_filter = fields.Datetime.to_string(begin_utc)
            offer.datetime_end_filter = fields.Datetime.to_string(end_utc)
            offer.date_begin_calendar = offer.date_begin
            offer.date_end_calendar = fields.Datetime.to_string(calendar_end)

    @api.multi
    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders')
        action = action.read()
        action['domain'] = str([('offer_id', 'in', self.ids)])
        return action

    def button_orderpoint(self, cr, uid, ids, context=None):
        raise NotImplementedError('not implemented')
        # TODO
        products = set()
        for offer in self.browse(cr, uid, ids, context=context):
            for position in offer.position_ids:
                for variant in position.variant_ids:
                    products.add(variant.product_id)
        orderpoint_ids = set()
        for product in products:
            for orderpoint in product.orderpoint_ids:
                orderpoint_ids.add(orderpoint.id)
        if not orderpoint_ids:
            raise exceptions.UserError(
                _('Error'),
                _('The products have no orderpoints configured.')
            )
        orderpoint_obj = self.pool['stock.warehouse.orderpoint']
        procurement_obj = self.pool['procurement.order']
        orderpoint_confirm = orderpoint_obj.procure_orderpoint_confirm
        procurement_ids = orderpoint_confirm(cr, uid, list(orderpoint_ids),
                                             context=context)
        purchase_ids = []
        procurements = procurement_obj.browse(cr, uid, procurement_ids,
                                              context=context)
        for procurement in procurements:
            if procurement.purchase_id:
                purchase_ids.append(procurement.purchase_id.id)
        return {
            'domain': "[('id', 'in', %s)]" % purchase_ids,
            'name': _('Generated Purchases'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
        }
