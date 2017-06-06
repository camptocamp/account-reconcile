# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import re
from datetime import datetime
from openerp import _, api, fields, models
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_TIME_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT,
                           )
from openerp.addons.mail.models import html2text
from string import Template
from openerp.exceptions import UserError


class CrmClaim(models.Model):
    _inherit = 'crm.claim'

    @api.multi
    def _get_message_quote(self):
        for claim in self:
            claim.message_quote_for_email = claim.message_quote(limit=2)

    @api.multi
    def _get_mail_signature(self):
        user = self.env.user
        for claim in self:
            if claim.partner_id.lang:
                claim_ctx = claim.with_context(lang=claim.partner_id.lang)
            template = ''
            if claim_ctx.qoqa_shop_id and \
                    claim_ctx.qoqa_shop_id.mail_signature_template:
                template = claim_ctx.qoqa_shop_id.mail_signature_template
            elif claim_ctx.company_id and \
                    claim_ctx.company_id.mail_signature_template:
                template = claim_ctx.company_id.mail_signature_template

            t = Template(template)
            user_signature = "The crazy otter"
            if user.signature:
                user_signature = user.signature
            t = t.safe_substitute(user_signature=user_signature,
                                  user_email=user.email)
            claim.mail_signature = t

    # extends field from crm_claim_code to add index
    code = fields.Char(index=True)
    # field used to keep track of the claims merged into this one,
    # so a the failsafe method that link emails from the number
    # can keep working based on the old numbers
    merged_numbers = fields.Serialized(
        string='Merged claims numbers'
    )
    message_quote_for_email = fields.Html(
        compute=_get_message_quote,
        string='Message quote'
    )
    mail_signature = fields.Html(
        compute=_get_mail_signature,
        string='Mail signature'
    )
    confirmation_email_template = fields.Many2one(
        comodel_name='mail.template',
        string='Confirmation Mail Template'
    )
    # The flag is set to false when the claim is created from an
    # email, this is to avoid to send an email on claims created
    # manually.
    confirmation_email_sent = fields.Boolean(
        string='Confirmation Mail Sent',
        default=True
    )
    last_message_date = fields.Datetime(
        string='Date of last message sent or received')

    @api.multi
    def _complete_from_sale(self, message):
        body = message.get('body')
        if not body:
            return message, None
        company = self.env.user.company_id
        pattern = company.claim_sale_order_regexp
        if not pattern:
            return message, None
        # find sales order's number
        pattern = re.compile(pattern, re.MULTILINE | re.UNICODE)
        number = re.search(pattern, body)
        if not number:
            return message, None
        number = number.group(1)
        sale_obj = self.env['sale.order']
        # In order to avoid dependency on connector_qoqa, and
        # to allow this search to be compatible with other sale
        # channels, we do not search in qoqa.sale.order but right
        # in the name of the sale order. Since the connector pads
        # the numbers with 0, make the same thing and search the name
        # for an exact match (eg it does not comes from the QoQa backend)
        # or padded (it comes from the QoQa backend).
        pad_number = '{0:08d}'.format(int(number))
        sale = sale_obj.search(
            ['|', ('name', '=', number), ('name', '=', pad_number)],
            limit=1)
        if not sale:
            return message, None
        invoice = sale._last_invoice()
        if not invoice:
            return message, None
        values = {'invoice_id': invoice.id,
                  'date': fields.Datetime.now(),
                  'company_id': company.id}
        partner = invoice.partner_id.commercial_partner_id
        values.setdefault('partner_id', partner.id)
        values.setdefault('partner_phone', partner.phone)
        # create temp claim to have onchange values
        temp_claim = self.with_context(create_lines=True).new(values)
        temp_claim._onchange_invoice_warehouse_type_date()
        values = temp_claim._convert_to_write(temp_claim._cache)

        return message, values

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
        through message_process.

        This set the confirmation_email_sent to False so an automatic email
        can be sent.
        Also write the field "last_message_date".
        """
        if custom_values is None:
            custom_values = {}
        else:
            custom_values = custom_values.copy()
        custom_values.setdefault('confirmation_email_sent', False)
        custom_values.setdefault('last_message_date', fields.Datetime.now())
        msg, values = self._complete_from_sale(msg)
        if values:
            custom_values.update(values)
        custom_values['description'] = False
        return super(CrmClaim, self).message_new(
            msg, custom_values=custom_values)

    @api.multi
    def _merge_data(self, oldest, fields):
        result = super(CrmClaim, self)._merge_data(oldest, fields)
        numbers = oldest.merged_numbers or []
        for claim in self:
            numbers.append(claim.code)
            if claim.merged_numbers:
                numbers += claim.merged_numbers
        result['merged_numbers'] = numbers
        return result

    @api.model
    def _merge_fields(self):
        merge_fields = super(CrmClaim, self)._merge_fields()
        if 'merged_numbers' in merge_fields:
            merge_fields.remove('merged_numbers')
        return merge_fields

    @api.multi
    def forge_original_message(self):
        self.ensure_one()
        return self.env['mail.message'].new({
            'date': self.date,
            'author_id': self.partner_id,
            'body': self.description or '',
        })

    @api.multi
    def message_quote(self, limit=None):
        """ For a claim, generate a thread with quotations.

        It converts HTML to text (markdown style) and prepend
        the messages with '>' characters.

        Example with 2 emails::

            On 2014-04-30 15:12:05, Deep Thought wrote:
            > Six by nine. Forty two.
            > On 2014-04-30 15:10:00, Arthur Dent wrote:
            >> What do you get if you multiply six by nine?

        """
        self.ensure_one()
        message_obj = self.env['mail.message']
        lang_obj = self.env['res.lang']
        messages = message_obj.search(
            [('res_id', '=', self.id),
             ('model', '=', self._name),
             ('message_type', '=', 'email'),
             ('subtype_id', '!=', False),
             ],
            order='date asc',
            limit=limit)
        if not messages:
            # build a message with the content of the claim
            messages = self.forge_original_message()
        if not messages:
            return ''
        else:
            lang = self.env.user.lang
            if not lang:
                lang = 'en_US'
            lang = lang_obj.search([('code', '=', lang)], limit=1)
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
                if message.id:
                    plain = html2text.html2text(message.body).split('\n')
                else:
                    # Special case for the 'original message' we just crafted
                    # above.  The content is already in text.
                    # But as MailMessage.body is of type Html, it surrounds the
                    # text with a <p> element, that we chop off of the string.
                    # 3 is the len of '<p>' and 4 of '</p>'
                    plain = message.body[3:-4].splitlines()
                plain += body
                body = [header] + ['&gt; %s' % line for line in plain]

            body = '<br/>'.join(body)
            return body

    @api.multi
    @api.returns('self', lambda value: value.id)
    def message_post(self, body='', subject=None, message_type='notification',
                     subtype=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        # Unsubscribe original author
        original_email_partner = False
        original_email_from = kwargs.pop('email_from', None)
        original_author_id = kwargs.pop('author_id', None)
        if original_author_id:
            self.message_unsubscribe([original_author_id])
        elif original_email_from:
            # Since [False] can be returned, only keep "real" ids
            original_email_partner = [
                partner
                for partner
                in self._find_partner_from_emails([original_email_from])
                if partner]
            self.message_unsubscribe(original_email_partner)

        # change author to partner with address 'loutres@qoqa.com'
        author_ids = self._find_partner_from_emails(['loutres@qoqa.com'])
        if not author_ids:
            raise UserError(_('No partner set with email "loutres@qoqa.com"'))
        # Use "mail_create_nosubscribe" in context to avoid having
        # "loutres" as follower
        result = super(CrmClaim, self.with_context(
            mail_create_nosubscribe=True)).message_post(
            body=body, subject=subject, message_type=message_type,
            subtype=subtype, parent_id=parent_id, attachments=attachments,
            content_subtype=content_subtype, author_id=author_ids[0],
            email_from='Loutres <loutres@qoqa.com>', **kwargs)

        # Re-subscribe original authors
        if original_author_id:
            self.message_subscribe([original_author_id])
        elif original_email_partner:
            self.message_subscribe(original_email_partner)

        # Use case : only close if email, if not the "assigned to you" email,
        # and if it does not come from the catchall
        if message_type == 'comment' and 'subtype_id' not in kwargs:
            self.case_close()
            # Also write the field "last_message_date".
            self.write({'last_message_date': fields.datetime.now()})
        return result
