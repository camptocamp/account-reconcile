# -*- coding: utf-8 -*-
#    Author: Leonardo Pistone
#    Copyright 2015 Camptocamp SA
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

import itertools

from openerp.osv import fields, orm
from openerp.tools.translate import _


class VariantGenerator(orm.TransientModel):
    _name = "variant.generator.wizard"
    _description = "Variant generator wizard"

    _columns = {
        'first_type_id': fields.many2one(
            'product.variant.dimension.type',
            'Type'
        ),
        'first_option_ids': fields.many2many(
            'product.variant.dimension.option',
            'first_wizard_option_rel',
            string='Options',
            domain="[('type_id', '=', first_type_id)]",
        ),
        'second_type_id': fields.many2one(
            'product.variant.dimension.type',
            'Type'
        ),
        'second_option_ids': fields.many2many(
            'product.variant.dimension.option',
            'second_wizard_option_rel',
            string='Options',
            domain="[('type_id', '=', second_type_id)]",
        ),
        'third_type_id': fields.many2one(
            'product.variant.dimension.type',
            'Type'
        ),
        'third_option_ids': fields.many2many(
            'product.variant.dimension.option',
            'third_wizard_option_rel',
            string='Options',
            domain="[('type_id', '=', third_type_id)]",
        ),
        'fourth_type_id': fields.many2one(
            'product.variant.dimension.type',
            'Type'
        ),
        'fourth_option_ids': fields.many2many(
            'product.variant.dimension.option',
            'fourth_wizard_option_rel',
            string='Options',
            domain="[('type_id', '=', fourth_type_id)]",
        ),
        'disable_original_product': fields.boolean(
            'Disable the original product'
        ),
    }

    def generate(self, cr, uid, ids, context):
        Product = self.pool['product.product']

        for wizard in self.browse(cr, uid, ids, context):
            product = Product.browse(cr, uid, context['active_id'], context)

            options = [wizard.first_option_ids]
            if wizard.second_option_ids:
                options.append(wizard.second_option_ids)
            if wizard.third_option_ids:
                options.append(wizard.third_option_ids)
            if wizard.fourth_option_ids:
                options.append(wizard.fourth_option_ids)

            combinations = itertools.product(*options)

            new_variant_ids = []
            for combination in combinations:
                new_data = {
                    'variants': ' - '.join(o.name for o in combination),
                    'default_code': ' - '.join(
                        [product.default_code] + [o.code for o in combination]
                    ),
                }
                new_ctx = context.copy()
                new_ctx['view_is_product_variant'] = True
                new_variant_ids.append(
                    Product.copy(cr, uid, product.id, default=new_data,
                                 context=new_ctx)
                )

            if wizard.disable_original_product:
                product.write({'active': False})

            new_variant_ids.append(product.id)

            ModelData = self.pool['ir.model.data']
            view_xmlid = ('product', 'product_variant_tree_view')
            __, view_id = ModelData.get_object_reference(cr, uid, *view_xmlid)
            return {
                'domain': [('id', 'in', new_variant_ids)],
                'name': _('Generated variants'),
                'view_type': 'form',
                'views': [(view_id, 'tree'), (False, 'form')],
                'res_model': 'product.product',
                'type': 'ir.actions.act_window',
            }
