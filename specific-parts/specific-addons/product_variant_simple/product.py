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

    def copy_translations(self, cr, uid, old_id, new_id, context=None):
        """ When we do not copy the template along the variant,
        copy_translations sometimes receives 2 identical IDs.

        That's because the ORM follows the o2m to copy the translations,
        so in that case, it follows 'variant_ids' and for each variant,
        it copy the translations. One of the variant is the 'new_id'.

        Just skip it.
        """
        if context.get('view_is_product_variant'):
            return
        super(product_template, self).copy_translations(
            cr, uid, old_id, new_id, context=context)


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

    def _copy_translation_no_inherits(self, cr, uid, old_id, new_id,
                                      context=None):
        """ Copy the translation of the current model, not following the
        inherits.

        Nearly a copy of ``copy_translations``, but skip all the
        inherits fields because the inherits'ed records have not been
        copied. If we were using the normal method, the translations of
        the ``_inherits`` would have been copied again and again (x2 at
        each duplicate).

        """
        if context is None:
            context = {}
        # avoid recursion through already copied records in case of
        # circular relationship
        seen_map = context.setdefault('__copy_translations_seen', {})
        if old_id in seen_map.setdefault(self._name, []):
            return
        seen_map[self._name].append(old_id)

        trans_obj = self.pool.get('ir.translation')
        # TODO it seems fields_get can be replaced by _all_columns (no
        # need for translation)
        fields = self.fields_get(cr, uid, context=context)

        for field_name, field_def in fields.items():
            # removing the lang to compare untranslated values
            context_wo_lang = dict(context, lang=None)
            old_record, new_record = self.browse(cr, uid, [old_id, new_id],
                                                 context=context_wo_lang)
            # we must recursively copy the translations for o2o and o2m
            if field_def['type'] == 'one2many':
                target_obj = self.pool.get(field_def['relation'])
                # here we rely on the order of the ids to match the
                # translations as foreseen in copy_data()
                old_children = sorted(r.id for r in old_record[field_name])
                new_children = sorted(r.id for r in new_record[field_name])
                for (old_child, new_child) in zip(old_children, new_children):
                    target_obj.copy_translations(cr, uid, old_child, new_child,
                                                 context=context)
            # and for translatable fields we keep them for copy
            elif field_def.get('translate'):
                if field_name in self._columns:
                    trans_name = self._name + "," + field_name
                    target_id = new_id
                    source_id = old_id
                else:  # inherits
                    continue

                trans_ids = trans_obj.search(cr, uid, [
                    ('name', '=', trans_name),
                    ('res_id', '=', source_id)
                ])
                user_lang = context.get('lang')
                for record in trans_obj.read(cr, uid, trans_ids,
                                             context=context):
                    del record['id']
                    # remove source to avoid triggering _set_src
                    del record['source']
                    record.update({'res_id': target_id})
                    if user_lang and user_lang == record['lang']:
                        # 'source' to force the call to _set_src
                        # 'value' needed if value is changed in copy(),
                        # want to see the new_value
                        record['source'] = old_record[field_name]
                        record['value'] = new_record[field_name]
                    trans_obj.create(cr, uid, record, context=context)

    def copy_translations(self, cr, uid, old_id, new_id, context=None):
        """ When we do not copy the template along the variant,
        copy_translations sometimes receives 2 identical IDs.

        That's because the ORM follows the o2m to copy the translations,
        so in that case, it follows 'variant_ids' and for each variant,
        it copy the translations. One of the variant is the 'new_id'.

        Just skip it.
        """
        if context is None:
            context = {}
        if context.get('view_is_product_variant'):
            if old_id == new_id:
                return
            self._copy_translation_no_inherits(cr, uid, old_id, new_id,
                                               context=context)

        else:
            super(product_product, self).copy_translations(
                cr, uid, old_id, new_id, context=context)
