# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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

import openerp.addons.decimal_precision as dp
from openerp.osv import orm, fields

class SaleDealVariant(orm.Model):
    _name = 'sale.deal.variant'
    _description = 'Sale Deal Variant'


    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True, ondelete='cascade'),
        'deal_id': fields.many2one('sale.deal', 'Deal', required=True, ondelete='cascade'),
        'sequence': fields.integer('Sequence'),
        'stock_available': fields.integer('Disponible'),
        'stock_reserved': fields.integer('Reservé'),
        # XXX sum sale orders (related to this deal)
        'stock_sold': fields.integer('Vendu'),
        'stock_residual': fields.integer('Solde'),
        # XXX compute percent
        'stock_progress': fields.float('Stock Progress'),
        }


class SaleDeal(orm.Model):

    _name = 'sale.deal'
    _description = 'Sale Deal'
    _inherit = ['mail.thread']

    _order = 'date_begin'

    _columns = {
        'name': fields.integer('Numéro de Planning'),
        'description': fields.text('Description',translate=True),
        'product_tmpl_id': fields.many2one('product.template', 'Product', required=True, readonly=True, states={'draft': [('readonly', False)]}, ondelete='set null', select=True),
        'variant_ids': fields.one2many('sale.deal.variant', 'deal_id', 'Product variants'),
        'date_begin': fields.datetime('Start Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date_end': fields.datetime('End Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'site': fields.selection([
            ('qoqa', 'QoQa'),
            ('qwine', 'QWine'),
            ('qstyle', 'QStyle'),
            ('qsport', 'QSport')],
            'Site concerné', required=True),
        'price_sale': fields.float('Prix de vente', required=True, digits_compute= dp.get_precision('Product Price')),
        'price_recommended': fields.float('Prix Conseillé', required=True, digits_compute= dp.get_precision('Product Price')),
        'price_observed': fields.float('Prix Constaté', required=True, digits_compute= dp.get_precision('Product Price')),
        'shipping_type': fields.selection([
            ('express', 'Express'),
            ('standard', 'standard')],
            'Type expédition', required=True),
        'shipping_costs': fields.float('Montant expédition', required=True, digits_compute= dp.get_precision('Product Price')),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, track_visibility='always'),
        # XXX sum of stock of variants
        'sum_stock_available': fields.integer('Stock disponible', help='Stock reservé chez le fournisseur'),
        # XXX sum of stock of variants
        'sum_stock_local': fields.integer('Stock local', help='Stock reservé chez le fournisseur'),
        'image': fields.binary("Image",
            help="This field holds the image used as image for the product, limited to 1024x1024px."),
        #'image_small': fields.function(_get_image, fnct_inv=_set_image,
            #string="Small-sized image", type="binary", multi="_get_image",
            #store={
                #'product.product': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            #},
            #help="Small-sized image of the product. It is automatically "\
                 #"resized as a 64x64px image, with aspect ratio preserved. "\
                 #"Use this field anywhere a small image is required."),
        'state': fields.selection([
            ('draft', 'Proposition'),
            ('open', 'Négociation'),
            ('cancel', 'Annulé'),
            ('confirm', 'Planifié'),
            ('done', 'Terminé')],
            'Status', readonly=True, required=True,
            track_visibility='onchange',
            help='If event is created, the status is \'Draft\'.If event is confirmed for the particular dates the status is set to \'Confirmed\'. If the event is over, the status is set to \'Done\'.If event is cancelled the status is set to \'Cancelled\'.'),
        'company_id': fields.many2one('res.company', 'Company', required=False, change_default=True, readonly=False, states={'done': [('readonly', True)]}),


        # Indicateurs
        'shipping_max_delay': fields.integer('Délai expédition max.', help='Stock reservé chez le fournisseur'),
        #'shipping_max_delay': fields.datetime('Délai expédition max.', readonly=True, states={'draft': [('readonly', False)]}),


        }

    _defaults = {
        'state': 'draft',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'event.event', context=c),
        #'user_id': lambda obj, cr, uid, context: uid,
    }
