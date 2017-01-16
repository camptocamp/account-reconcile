# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class Contact(models.AbstractModel):
    _inherit = 'ir.qweb.field.contact'

    @api.model
    def record_to_html(self, field_name, record, options=None):
        _super = super(Contact, self)
        return _super.record_to_html(
            field_name,
            record.with_context(_name_get_report=True),
            options=options,
        )
