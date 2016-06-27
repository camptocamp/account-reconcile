# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp.addons.mail.tests.common import TestMail
from openerp.addons.mail.tests.test_mail_gateway import MAIL_TEMPLATE


class TestMailThread(TestMail):

    @staticmethod
    def format(template, to='Claims <claims@example.com>', cc='',
               subject='1', extra='',
               email_from='Sylvie Lelitre <test.sylvie.lelitre@agrolait.com>',
               msg_id=''):
        return template.format(to=to, cc=cc, subject=subject, extra=extra,
                               email_from=email_from, msg_id=msg_id)

    def setUp(self):
        super(TestMailThread, self).setUp()
        partner = self.browse_ref('base.res_partner_4')
        partner.write({'email': 'loutres@qoqa.com'})
        self.Claim = Claim = self.env['crm.claim']
        msg_id = '<1198923581.41972151344608186760.JavaMail@agrolait.com>'
        email = self.format(MAIL_TEMPLATE,
                            msg_id=msg_id)
        claim_id = Claim.message_process(Claim._name, email)
        self.claim = claim = Claim.browse(claim_id)
        # force the number to be in the format used by QoQa,
        # it must match with a regular expression to be found
        # in the mail routing
        self.claim.write({'number': 'RMA-123456'})
        self.claim.refresh()
        for message in sorted(claim.message_ids, key=lambda msg: msg.id):
            if message.subtype_id.name == 'Discussions':
                self.msg = message
                break

    def test_in_reply_to(self):
        """ Link with parent using In-Reply-To """

        msg_id = '<1198923581.41972151344608186760.JavaMail.1@agrolait.com>'
        reply_msg = self.format(MAIL_TEMPLATE, to='erroneous@example.com',
                                extra='In-Reply-To: %s' % self.msg.message_id,
                                msg_id=msg_id)
        self.Claim.message_process(None, reply_msg)
        self.assertReceived(nb_messages=4, nb_children=1)

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

        msg_id = '<1198923581.41972151344608186760.JavaMail.2@agrolait.com>'
        subject = "Re: [%s] 1" % self.claim.number
        reply_msg = self.format(MAIL_TEMPLATE, to='erroneous@example.com',
                                subject=subject,
                                msg_id=msg_id)
        self.Claim.message_process(None, reply_msg)
        self.assertReceived(nb_messages=4, nb_children=2)
