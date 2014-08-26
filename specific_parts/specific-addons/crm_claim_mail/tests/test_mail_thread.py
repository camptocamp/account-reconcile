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

from openerp.addons.mail.tests.test_mail_base import TestMailBase
from openerp.addons.mail.tests.test_mail_gateway import MAIL_TEMPLATE


class TestMailThread(TestMailBase):

    @staticmethod
    def format(template, to='Claims <claims@example.com>',
               subject='1', extra='',
               email_from='Sylvie Lelitre <test.sylvie.lelitre@agrolait.com>',
               msg_id=''):
        return template.format(to=to, subject=subject, extra=extra,
                               email_from=email_from, msg_id=msg_id)

    def setUp(self):
        super(TestMailThread, self).setUp()
        cr, uid = self.cr, self.uid
        self.Claim = Claim = self.registry('crm.claim')
        msg_id = '<1198923581.41972151344608186760.JavaMail@agrolait.com>'
        email = self.format(MAIL_TEMPLATE,
                            msg_id=msg_id)
        claim_id = Claim.message_process(cr, uid, Claim._name, email)
        self.claim = claim = Claim.browse(cr, uid, claim_id)
        self.msg = claim.message_ids[0]

    def test_in_reply_to(self):
        """ Link with parent using In-Reply-To """
        cr, uid = self.cr, self.uid

        msg_id = '<1198923581.41972151344608186760.JavaMail.1@agrolait.com>'
        reply_msg = self.format(MAIL_TEMPLATE, to='erroneous@example.com',
                                extra='In-Reply-To: %s' % self.msg.message_id,
                                msg_id=msg_id)
        self.Claim.message_process(cr, uid, None, reply_msg)
        self.assertReceived(nb_messages=2, nb_children=1)

    def assertReceived(self, nb_messages, nb_children):
        self.claim.refresh()
        self.msg.refresh()
        self.assertEqual(nb_messages, len(self.claim.message_ids),
                         'message_process: claim should contain %d messages' %
                         nb_messages)
        self.assertEqual(nb_children, len(self.msg.child_ids),
                         'message_process: message should have %d children' %
                         nb_children)

    def test_claim_number(self):
        """ Link with parent using number of the claim """
        cr, uid = self.cr, self.uid

        msg_id = '<1198923581.41972151344608186760.JavaMail.2@agrolait.com>'
        subject = "Re: [%s] 1" % self.claim.number
        reply_msg = self.format(MAIL_TEMPLATE, to='erroneous@example.com',
                                subject=subject,
                                msg_id=msg_id)
        self.Claim.message_process(cr, uid, None, reply_msg)
        self.assertReceived(nb_messages=2, nb_children=1)
