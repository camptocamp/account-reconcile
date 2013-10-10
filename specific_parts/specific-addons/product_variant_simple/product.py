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


class product_template(orm.Model):
    _inherit = 'product.template'
    _columns = {
        'variant_ids': fields.one2many(
            'product.product',
            'product_tmpl_id',
            string='Variants'),
    }


class product_product(orm.Model):
    _inherit = 'product.product'

    def copy_data(self, cr, uid, id, default=None, context=None):
        """ When we duplicate a variant (from the variant view),
        we except the template not to be duplicated.

        So we set the ``product_tmpl_id`` field on the product, but
        we have also to remove all the fields related to the template
        from the ``default`` otherwise we'll empty values of the template.
        """
        if context is None:
            context = {}
        if default is None:
            default = {}
        is_variant = context.get('view_is_product_variant')
        if is_variant:
            tmpl_obj = self.pool.get('product.template')
            product = self.browse(cr, uid, id, context=context)
            default['product_tmpl_id'] = product.product_tmpl_id.id

        data = super(product_product, self).copy_data(
            cr, uid, id, default=default, context=context)

        if is_variant:
            # remove all the fields from product.template
            blacklist = set(tmpl_obj._all_columns) - set(self._columns)
            data = dict((key, value) for key, value in data.iteritems()
                        if key not in blacklist)
        return data

    def copy_translations(self, cr, uid, old_id, new_id, context=None):
        """ When we do not copy the template along the variant,
        copy_translations sometimes receives 2 identical IDs.

        That's because the ORM follows the o2m to copy the translations,
        so in that case, it follows 'variant_ids' and for each variant,
        it copy the translations. One of the variant is the 'new_id'.

        Just skip it.
        """
        if context.get('view_is_product_variant') and old_id == new_id:
            return
        super(product_product, self).copy_translations(
            cr, uid, old_id, new_id, context=context)
