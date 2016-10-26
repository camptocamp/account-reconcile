# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from openerp.addons.base.ir.ir_qweb import escape, HTMLSafe


class Contact(models.AbstractModel):
    _inherit = 'ir.qweb.field.contact'

    def record_to_html(self, cr, uid, field_name, record, options=None,
                       context=None):
        # Redefine widget as the name_get() was overridden by specific_fct
        if context is None:
            context = {}

        if options is None:
            options = {}
        opf = options.get('fields') or ["name", "address", "phone",
                                        "mobile", "fax", "email"]

        value_rec = record[field_name]
        if not value_rec:
            return None
        value_rec = value_rec.sudo().with_context(show_address=True)
        value = value_rec.name_get()[0][1]
        # Call display_address to have it with line breaks
        address = value_rec._display_address(value_rec)

        # Use the new format with ", " as separator
        val = {
            'name': value.split(", ")[0],
            'address': escape(address.replace("\n\n", "\n")).strip(),
            'phone': value_rec.phone,
            'mobile': value_rec.mobile,
            'fax': value_rec.fax,
            'city': value_rec.city,
            'country_id': value_rec.country_id.display_name,
            'website': value_rec.website,
            'email': value_rec.email,
            'fields': opf,
            'object': value_rec,
            'options': options
        }

        html = self.pool["ir.ui.view"].render(cr, uid, "base.contact",
                                              val, engine='ir.qweb',
                                              context=context).decode('utf8')

        return HTMLSafe(html)
