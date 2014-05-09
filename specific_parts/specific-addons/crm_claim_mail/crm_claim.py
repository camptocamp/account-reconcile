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
from datetime import datetime
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT,
                           DEFAULT_SERVER_TIME_FORMAT,
                           DEFAULT_SERVER_DATETIME_FORMAT,
                           )
from openerp.addons.email_template import html2text


class crm_claim(orm.Model):
    _inherit = 'crm.claim'

    def _get_message_quote(self, cr, uid, ids, fields, args, context=None):
        result = {}
        for claim_id in ids:
            result[claim_id] = self.message_quote(cr, uid, claim_id,
                                                  context=context)
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
        'confirmation_email_sent': fields.boolean('Confirmation Mail Sent'),
    }

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

    def message_quote(self, cr, uid, id, context=None):
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
             ],
            order='date asc',
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
