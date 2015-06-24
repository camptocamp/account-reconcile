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

from openerp.osv import fields, orm


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
            string='Options',
            domain="[('type_id', '=', first_type_id)]",
        ),
        'second_type_id': fields.many2one(
            'product.variant.dimension.type',
            'Type'
        ),
        'second_option_ids': fields.many2many(
            'product.variant.dimension.option',
            string='Options',
            domain="[('type_id', '=', second_type_id)]",
        ),
        'third_type_id': fields.many2one(
            'product.variant.dimension.type',
            'Type'
        ),
        'third_option_ids': fields.many2many(
            'product.variant.dimension.option',
            string='Options',
            domain="[('type_id', '=', third_type_id)]",
        ),
    }
