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
from datetime import datetime
from operator import attrgetter
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_TIME_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT,
                           )
from openerp.addons.email_template import html2text
from string import Template


class crm_claim(orm.Model):
    _inherit = 'crm.claim'

    def _get_message_quote(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for claim_id in ids:
            result[claim_id] = self.message_quote(cr, uid, claim_id,
                                                  limit=2, context=context)
        return result

    def _get_mail_signature(self, cr, uid, ids, fields, args, context=None):
        if context is None:
            context = {}
        claims = self.browse(cr, uid, ids, context=context)
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        result = {}
        for claim in claims:
            lang = claim.partner_id.lang
            ctx = context.copy()

            if lang:
                ctx['lang'] = lang

            claim = self.browse(cr, uid, claim.id, context=ctx)
            template = ''
            if claim.shop_id and claim.shop_id.mail_signature_template:
                template = claim.shop_id.mail_signature_template
            else:
                template = claim.company_id.mail_signature_template

            t = Template(template)
            user_signature = "The crazy otter"
            if user.signature:
                user_signature = user.signature
            t = t.safe_substitute(user_signature=user_signature,
                                  user_email=user.email)
            result[claim.id] = t

        return result

    _columns = {
        # should always be readonly since it is used to match
        # incoming emails
        'number': fields.char(
            'Number', readonly=True,
            required=True,
            select=True,
            help="Company internal claim unique number"),
        # field used to keep track of the claims merged into this one,
        # so a the failsafe method that link emails from the number
        # can keep working based on the old numbers
        'merged_numbers': fields.serialized('Merged claims numbers'),
        'message_quote_for_email': fields.function(
            _get_message_quote,
            type='html',
            string='Message quote'),
        'mail_signature': fields.function(
            _get_mail_signature,
            type='html',
            string='Mail signature'),
        'confirmation_email_sent': fields.boolean('Confirmation Mail Sent'),
    }

    _defaults = {
        # The flag is set to false when the claim is created from an
        # email, this is to avoid to send an email on claims created
        # manually.
        'confirmation_email_sent': True,
    }

    def _complete_from_sale(self, cr, uid, message, context=None):
        body = message.get('body')
        if not body:
            return message, None
        user_obj = self.pool['res.users']
        user = user_obj.browse(cr, uid, uid, context=context)
        company = user.company_id
        pattern = company.claim_sale_order_regexp
        if not pattern:
            return message, None
        # find sales order's number
        pattern = re.compile(pattern, re.MULTILINE | re.UNICODE)
        number = re.search(pattern, body)
        if not number:
            return message, None
        number = number.group(1)
        sale_obj = self.pool['sale.order']
        # In order to avoid dependency on connector_qoqa, and
        # to allow this search to be compatible with other sale
        # channels, we do not search in qoqa.sale.order but right
        # in the name of the sale order. Since the connector pads
        # the numbers with 0, make the same thing and search the name
        # for an exact match (eg it does not comes from the QoQa backend)
        # or padded (it comes from the QoQa backend).
        pad_number = '{0:08d}'.format(int(number))
        sale_ids = sale_obj.search(cr, uid,
                                   ['|',
                                    ('name', '=', number),
                                    ('name', '=', pad_number),
                                    ],
                                   context=context)
        if not sale_ids:
            return message, None
        sale = sale_obj.browse(cr, uid, sale_ids[0], context=context)
        invoices = (invoice for invoice in sale.invoice_ids
                    if invoice.state != 'cancel')
        invoices = sorted(invoices, key=attrgetter('date_invoice'),
                          reverse=True)
        if not invoices:
            return message, None
        invoice = invoices[0]
        values = {'invoice_id': invoice.id}
        res = self.onchange_invoice_id(cr, uid, [], invoice.id,
                                       values.get('warehouse_id'),
                                       'customer',
                                       fields.datetime.now(),
                                       company.id,
                                       [],
                                       create_lines=True,
                                       context=context)
        if res.get('value'):
            values.update(res['value'])
        values['claim_line_ids'] = [(0, 0, line) for line
                                    in values['claim_line_ids']
                                    ]
        partner = invoice.partner_id.commercial_partner_id
        values.setdefault('partner_id', partner.id)
        values.setdefault('partner_phone', partner.phone)

        return message, values

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
        through message_process.

        This set the confirmation_email_sent to False so an automatic email
        can be sent.

        """
        if custom_values is None:
            custom_values = {}
        else:
            custom_values = custom_values.copy()
        custom_values.setdefault('confirmation_email_sent', False)
        msg, values = self._complete_from_sale(cr, uid, msg, context=context)
        if values:
            custom_values.update(values)
        return super(crm_claim, self).message_new(
            cr, uid, msg, custom_values=custom_values, context=context)

    def _merge_data(self, cr, uid, merge_in, claims, fields, context=None):
        result = super(crm_claim, self)._merge_data(
            cr, uid, merge_in, claims, fields, context=context)
        numbers = merge_in.merged_numbers or []
        for claim in claims:
            numbers.append(claim.number)
            if claim.merged_numbers:
                numbers += claim.merged_numbers
        result['merged_numbers'] = numbers
        return result

    def _merge_fields(self, cr, uid, context=None):
        merge_fields = super(crm_claim, self)._merge_fields(
            cr, uid, context=context)
        if 'merged_numbers' in merge_fields:
            merge_fields.remove('merged_numbers')
        return merge_fields

    def message_quote(self, cr, uid, id, limit=None, context=None):
        """ For a claim, generate a thread with quotations.

        It converts HTML to text (markdown style) and prepend
        the messages with '>' characters.

        Example with 2 emails::

            On 2014-04-30 15:12:05, Deep Thought wrote:
            > Six by nine. Forty two.
            > On 2014-04-30 15:10:00, Arthur Dent wrote:
            >> What do you get if you multiply six by nine?

        """
        if isinstance(id, (tuple, list)):
            assert len(id) == 1, "1 ID expected, got: %s" % id
            id = id[0]
        message_obj = self.pool['mail.message']
        user_obj = self.pool['res.users']
        lang_obj = self.pool['res.lang']
        message_ids = message_obj.search(
            cr, uid,
            [('res_id', '=', id),
             ('model', '=', self._name),
             ('type', 'in', ('email', 'comment')),
             ('subtype_id', '!=', False),
             ],
            order='date asc',
            limit=limit,
            context=context)
        if not message_ids:
            return ''
        else:
            messages = message_obj.browse(cr, uid, message_ids,
                                          context=context)
            user = user_obj.browse(cr, uid, uid, context=context)
            lang = user.lang
            if not lang:
                lang = 'en_US'
            lang_ids = lang_obj.search(cr, uid, [('code', '=', lang)],
                                       context=context)
            lang = lang_obj.browse(cr, uid, lang_ids[0], context=context)
            date_fmt = lang.date_format or DEFAULT_SERVER_DATE_FORMAT
            time_fmt = lang.time_format or DEFAULT_SERVER_TIME_FORMAT
            body = []
            for message in messages:
                msg_date = datetime.strptime(message.date,
                                             DEFAULT_SERVER_DATETIME_FORMAT)
                msg_date_f = msg_date.strftime(date_fmt)
                msg_time_f = msg_date.strftime(time_fmt)
                header = _('On %s at %s, %s wrote:') % (msg_date_f,
                                                        msg_time_f,
                                                        message.author_id.name)
                plain = html2text.html2text(message.body).split('\n')
                plain += body
                body = [header] + ['&gt; %s' % line for line in plain]

            body = '<br/>'.join(body)
            return body

    def case_closed(self, cr, uid, ids, context=None):
        """ Mark the claim as closed: state=done """
        if isinstance(ids, (int, long)):
            ids = [ids]
        for claim in self.browse(cr, uid, ids, context=context):
            stage_id = self.stage_find(cr, uid, [claim],
                                       claim.section_id.id or False,
                                       [('state', '=', 'done')],
                                       context=context)
            if stage_id:
                self.case_set(cr, uid, [claim.id], values_to_update={},
                              new_stage_id=stage_id, context=context)
        return True

    def message_post(self, cr, uid, thread_id, body='', subject=None,
                     type='notification', subtype=None, parent_id=False,
                     attachments=None, context=None,
                     content_subtype='html', **kwargs):
        result = super(crm_claim, self).message_post(
            cr, uid, thread_id, body=body, subject=subject, type=type,
            subtype=subtype, parent_id=parent_id, attachments=attachments,
            context=context, content_subtype=content_subtype, **kwargs)
        if type == 'comment' and subtype:
            self.case_closed(cr, uid, thread_id, context=context)
        return result
