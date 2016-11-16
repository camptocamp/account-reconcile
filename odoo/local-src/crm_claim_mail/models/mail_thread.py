# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import re
import types
from lxml import html
from openerp import api, tools
from openerp.addons.mail.models.mail_thread import decode_header, MailThread


RMA_RE = re.compile(r".*\[(RMA-\d+|SOS-\d+)].*", re.UNICODE)


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
            message.get_payload(1).get_content_type() ==
            'message/delivery-status')


def claim_subject_route(mail_thread, message, custom_values=None):
    """ Link a message to an existing route using the reference
    in the subject """
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
        claim_obj = mail_thread.env['crm.claim']
        claim_ids = claim_obj.with_context(
            active_test=False).search([('code', '=', claim_number)]).ids
        if not claim_ids:
            cursor = mail_thread.env.cr
            # search also in merged claims
            pattern = '"%s"' % claim_number
            cursor.execute(
                "SELECT id FROM crm_claim "
                "WHERE merged_numbers ~ %s", (pattern,))
            claim_ids = [row[0] for row in cursor.fetchall()]
        if claim_ids:
            return [('crm.claim', claim_id, custom_values,
                     mail_thread._uid, None)
                    for claim_id in claim_ids]


# we need to monkey patch message_route because inheriting
# MailThread is not applied!
old_message_route = MailThread.message_route
old_message_parse = MailThread.message_parse


@api.model
def message_route(self, message, message_dict, model=None, thread_id=None,
                  custom_values=None):
    # first search if the email is a response to a claim with the
    # subject, then fallback on the other routes
    if not is_dsn(message):
        # If the subject contains [RMA-\d+], search for a claim
        routes = claim_subject_route(self, message,
                                     custom_values=custom_values)
        if routes:
            return routes
    return old_message_route(
        self, message, message_dict, model=model, thread_id=thread_id,
        custom_values=custom_values)


MailThread.message_route = types.MethodType(message_route, None, MailThread)


@api.model
def message_parse(self, message, save_original=False):
    msg_dict = old_message_parse(self, message, save_original)
    # If email_from = 'contact@qoqa.ch', this means that the email comes
    # from the website ; parse the body to retrieve the real address
    if 'contact@qoqa.ch' in msg_dict['email_from']:
        body = html.fromstring(msg_dict['body'])
        user_email = body.xpath('//b[text()="User :"]/../text()')
        if user_email:
            user_email = ', '.join(user_email)
            email_address = tools.email_split(user_email)[0]
            if email_address:
                msg_dict['from'] = email_address
                msg_dict['email_from'] = email_address
                partners = MailThread._find_partner_from_emails(
                    self, [email_address])
                if partners:
                    msg_dict['author_id'] = partners[0].id

    return msg_dict


MailThread.message_parse = types.MethodType(message_parse, None, MailThread)
