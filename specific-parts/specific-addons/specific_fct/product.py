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
from openerp.osv import orm, fields


class product_category(orm.Model):
    """
    Change default value to average on cost_method
    """
    _inherit = 'product.category'

    _columns = {
        'warranty': fields.float('Warranty'),
        'product_type': fields.selection(
            [('product', 'Stockable Product'),
             ('consu', 'Consumable'),
             ('service', 'Service')],
            'Product Type'),
    }

    _defaults = {
        'warranty': 24,
        'product_type': 'product',
    }


class product_template(orm.Model):
    """
    Change default value to average on cost_method
    """
    _inherit = 'product.template'

    def _get_variant_codes(self, cr, uid, ids, field_names, args,
                           context=None):
        res = {}
        for template in self.browse(cr, uid, ids, context=context):
            refs = ('[%s]' % product.default_code for product
                    in template.variant_ids if product.default_code)
            res[template.id] = ''.join(refs)
        return res

    def _template_from_variant_ids(self, cr, uid, ids, context=None):
        template_ids = set()
        product_obj = self.pool['product.product']
        for product in product_obj.browse(cr, uid, ids, context=context):
            template_ids.add(product.product_tmpl_id.id)
        return list(template_ids)

    _columns = {
        'variant_codes': fields.function(
            _get_variant_codes,
            string='Variants References',
            type='char',
            select=True,
            store={
                _inherit: (lambda s, c, u, ids, ctx: ids, ['variant_ids'], 20),
                'product.product': (_template_from_variant_ids,
                                    ['default_code', 'product_tmpl_id'], 20)
            }),
    }

    _defaults = {
        'cost_method': 'average',
        'company_id': False,
        'categ_id': False
    }

    def name_search(self, cr, uid, name='', args=None,
                    operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            # Do not merge the 2 next lines into one single search,
            # SQL search performance would be abysmal on a database
            # with thousands of matching products, due to the huge
            # merge+unique needed for the OR operator (and given the
            # fact that the 'name' lookup results come from the
            # ir.translation table Performing a quick memory merge
            # of ids in Python will give much better performance
            ids = set()
            ids.update(
                self.search(cr, uid,
                            args + [('variant_codes', operator, name)],
                            limit=limit, context=context)
            )
            if not limit or len(ids) < limit:
                # we may underrun the limit because of dupes in the
                # results, that's fine
                search_limit = limit - len(ids) if limit else False
                ids.update(
                    self.search(cr, uid,
                                args + [('name', operator, name)],
                                limit=search_limit,
                                context=context)
                )
            ids = list(ids)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        result = self.name_get(cr, uid, ids, context=context)
        return result

    def onchange_categ_id(self, cr, uid, ids, categ_id, context=None):
        if context is None:
            context = {}
        res = {'value': {}}

        if not categ_id:
            return res

        category = self.pool.get('product.category').browse(
            cr, uid, categ_id, context=context)
        res['value'].update({'warranty': category.warranty,
                             'type': category.product_type})
        return res


class product_product(orm.Model):
    """
    Do not copy the ean13 product code
    """
    _inherit = 'product.product'

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'ean13': False})
        return super(product_product, self).copy(cr, uid, id, default, context)

    def onchange_categ_id(self, cr, uid, ids, categ_id, context=None):
        if context is None:
            context = {}
        res = {'value': {}}

        if not categ_id:
            return res

        category = self.pool.get('product.category').browse(
            cr, uid, categ_id, context=context)
        res['value'].update({'warranty': category.warranty,
                             'type': category.product_type})
        return res

    def create(self, cr, uid, vals, context=None):
        # Create default orderpoint for product
        product_id = super(product_product, self).create(cr, uid, vals,
                                                         context=context)
        orderpoint_obj = self.pool['stock.warehouse.orderpoint']
        orderpoint_obj.create(cr, uid,
                              {'name': 'Approvisionnement Standard 1/1 U',
                               'product_id': product_id,
                               'product_min_qty': 0.0,
                               'product_max_qty': 0.0,
                               'product_uom': vals['uom_id']},
                              context=context)
        return product_id
