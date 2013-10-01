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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp



class qoqa_offer(orm.Model):
    _name = 'qoqa.offer'
    _description = 'QoQa Offer'

    REGULAR_PRICE_TYPE = [('normal', 'Normal Price'),
                          ('no_price', 'No Price'),
                          ('direct', 'Direct Price'),
                          ]

    _columns = {
        'deal_id': fields.many2one(
            'sale.deal',
            string='Deal',
            required=True),
        'product_tmpl_id': fields.many2one(
            'product.template',
            string='Product Template',
            required=True),
        'currency_id': fields.many2one(
            'res.currency',
            string='Currency',
            required=True),
        'vat_id': fields.many2one(
            'account.tax',
            string='VAT',
            required=True,
            domain="[('type_tax_use', '=', 'sale')]"),
        'lot_size': fields.integer('Lot Size', required=True),
        'max_sellable': fields.integer('Max Sellable', required=True),
        'stock_bias': fields.integer('Stock Bias'),
        'unit_price': fields.float(
            'Unit Price',
            digits_compute=dp.get_precision('Product Price'),
            required=True),
        'installment_price': fields.float(
            'Installment Price',
            digits_compute=dp.get_precision('Product Price')),
        'installment_price': fields.float(
            'Installment Price',
            digits_compute=dp.get_precision('Product Price'),
            required=True),
        'regular_price': fields.float(
            'Regular Price',
            digits_compute=dp.get_precision('Product Price'),
            required=True),
        'regular_price_type': fields.selection(
            'Regular Price Type',
            required=True),
        'buy_price': fields.float(
            'Buy Price',
            digits_compute=dp.get_precision('Product Price')),
        'top_price': fields.float(
            'Buy Price',
            digits_compute=dp.get_precision('Product Price')),
        'ecotax': fields.integer('Ecotax'),
        'date_delivery': fields.date('Delivery Date'),
        'booking_delivery': fields.boolean('Booking Delivery'),
        # TODO: many2one with phrases
        #'buyphrase_id': 
        'order_url': fields.char('Order URL'),
        'is_net_price': fields.boolean('Is Net Price'),
        'qoqa_active': fields.boolean('Active on QoQa'),
        # TODO: add linked product and variants
    }

    _defaults = {
        'regular_price_type': 'normal',
        'stock_bias': 100,
        'qoqa_active': True,
    }
