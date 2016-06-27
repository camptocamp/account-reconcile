# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import api, models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def get_record_data(self, values):
        result = super(MailComposeMessage, self).get_record_data(values)
        if values.get('model') == 'crm.claim' and values.get('res_id'):
            claim = self.env['crm.claim'].browse(values.get('res_id'))
            body = claim.message_quote(limit=2)
            if body:
                result['body'] = body
        return result
