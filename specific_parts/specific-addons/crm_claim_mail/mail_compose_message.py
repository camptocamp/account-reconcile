# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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


class mail_compose_message(orm.TransientModel):
    _inherit = 'mail.compose.message'

    def get_record_data(self, cr, uid, model, res_id, context=None):
        values = super(mail_compose_message, self).get_record_data(
            cr, uid, model, res_id, context=context)
        if model == 'crm.claim':
            claim_obj = self.pool[model]
            body = claim_obj.message_quote(cr, uid, res_id,limit=2, context=context)
            if body:
                values['body'] = body
        return values
