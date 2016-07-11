# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def _get_product_type(self):
        """ Get product types from template method """
        tmpl_obj = self.env['product.template']
        return tmpl_obj._get_product_template_type()

    warranty = fields.Float('Warranty', default=24)
    product_type = fields.Selection(
        'get_product_type',
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


class ProductProduct(models.Model):
    """ Do not copy the ean13 product code
    """
    _inherit = 'product.product'

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default.update({'ean13': False})
        return super(ProductProduct, self).copy(default)

    @api.onchange('categ_id')
    def onchange_categ_id(self):
        self.warranty = self.categ_id.warranty
        self.type = self.categ_id.product_type

    @api.model
    def create(self, vals):
        # Create default orderpoint for product
        product = super(ProductProduct, self).create(vals)
        if 'orderpoint_ids' not in vals:
            orderpoint_obj = self.env['stock.warehouse.orderpoint']
            orderpoint_obj.create({'name': 'Approvisionnement Standard 1/1 U',
                                   'product_id': product.id,
                                   'product_min_qty': 0.0,
                                   'product_max_qty': 0.0,
                                   'product_uom': product.uom_id.id})
        return product
