# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    warranty = fields.Float('Warranty', default=24)
    product_type = fields.Selection(
        [('product', 'Stockable Product'), ('consu', 'Consumable'),
         ('service', 'Service')],
        string='Product Type',
        default='product'
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    company_id = fields.Many2one(default=False)
    categ_id = fields.Many2one(default=False)

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        self.warranty = self.categ_id.warranty
        self.type = self.categ_id.product_type


# TODO:
# class ProductProduct(models.Model):
#     """ Do not copy the ean13 product code
#     """
#     _inherit = 'product.product'
#
#     def copy(self, cr, uid, id, default=None, context=None):
#         if default is None:
#             default = {}
#         default = default.copy()
#         default.update({'ean13': False})
#         return super(product_product, self).copy(cr, uid, id, default, context)
#
#     def onchange_categ_id(self, cr, uid, ids, categ_id, context=None):
#         if context is None:
#             context = {}
#         res = {'value': {}}
#
#         if not categ_id:
#             return res
#
#         category = self.pool.get('product.category').browse(
#             cr, uid, categ_id, context=context)
#         res['value'].update({'warranty': category.warranty,
#                              'type': category.product_type})
#         return res
#
#     def create(self, cr, uid, vals, context=None):
#         # Create default orderpoint for product
#         product_id = super(product_product, self).create(cr, uid, vals,
#                                                          context=context)
#         if 'orderpoint_ids' not in vals:
#             product = self.browse(cr, uid, product_id, context=context)
#             orderpoint_obj = self.pool['stock.warehouse.orderpoint']
#             orderpoint_obj.create(cr, uid,
#                                   {'name': 'Approvisionnement Standard 1/1 U',
#                                    'product_id': product_id,
#                                    'product_min_qty': 0.0,
#                                    'product_max_qty': 0.0,
#                                    'product_uom': product.uom_id.id},
#                                   context=context)
#         return product_id
