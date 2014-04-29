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

import re
import types
from openerp.addons.mail.mail_thread import decode_header, mail_thread


RMA_RE = re.compile(r".*\[(RMA-\d+)].*", re.UNICODE)

# we need to monkey patch message_route because inheriting
# mail_thread is not applied!
old_message_route = mail_thread.message_route
def message_route(self, cr, uid, message, model=None, thread_id=None,
                  custom_values=None, context=None):
    try:
        return old_message_route(
            self, cr, uid, message, model=model, thread_id=thread_id,
            custom_values=custom_values, context=context)
    except ValueError:  # no route found
        # If the subject contains [RMA-\d+], search for a claim
        subject = decode_header(message, 'Subject')
        match = RMA_RE.search(subject)
        if match:
            claim_number = match.group(1)
            claim_obj = self.pool['crm.claim']
            ctx = context.copy()
            ctx['active_test'] = False
            claim_ids = claim_obj.search(cr, uid,
                                         [('number', '=', claim_number)],
                                         context=ctx)
            if not claim_ids:
                # search also in merged claims
                pattern = '"%s"' % claim_number
                cr.execute("SELECT id FROM crm_claim "
                           "WHERE merged_numbers ~ %s", (pattern,))
                claim_ids = [row[0] for row in cr.fetchall()]
            if claim_ids:
                return [('crm.claim', claim_id, custom_values, uid)
                        for claim_id in claim_ids]
        raise

mail_thread.message_route = types.MethodType(message_route, None, mail_thread)
