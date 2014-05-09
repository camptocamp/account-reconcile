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

import email
import re
import types
from openerp.addons.mail.mail_thread import decode_header, mail_thread


RMA_RE = re.compile(r".*\[(RMA-\d+)].*", re.UNICODE)


def is_dsn(message):
    """ Returns True if `message` is a Delivery Status Notification

    According to RFC 3464, the Delivery Status Notifications are
    multipart messages composed of 3 parts (text/plain,
    message/delivery-status and message/rfc822).

    From: "Mail Delivery System" <MAILER-DAEMON@example.com> Subject:
    Delivery Status Notification (Failure) Content-Type:
    multipart/report; report-type=delivery-status

    Content-Type: text/plain A human readable explanation of the
    Delivery Status Notification.

    Content-Type: message/delivery-status A structured machine readable
    reason for the Delivery Status Notification.

    Content-Type: message/rfc822 The original message.

    """
    return (message.is_multipart() and len(message.get_payload()) > 1 and
            message.get_payload(1).get_content_type() == 'message/delivery-status')


def claim_subject_route(mail_thread, cr, uid, message, custom_values=None,
                        context=None):
    """ Link a message to an existing route using the reference in the
    subject """
    if custom_values is None:
        custom_values = {}

    return_path = decode_header(message, 'Return-Path')
    if return_path.strip() == '<>':
        # automated email such as auto-reply use the
        # Return-Path: <> header, do not send them an email
        custom_values = custom_values.copy()
        custom_values['confirmation_email_sent'] = True

    subject = decode_header(message, 'Subject')
    match = RMA_RE.search(subject)
    if match:
        claim_number = match.group(1)
        claim_obj = mail_thread.pool['crm.claim']
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
        if not is_dsn(message):
            routes = claim_subject_route(self, cr, uid, message,
                                         custom_values=custom_values,
                                         context=context)
            if routes:
                return routes
        raise

mail_thread.message_route = types.MethodType(message_route, None, mail_thread)
