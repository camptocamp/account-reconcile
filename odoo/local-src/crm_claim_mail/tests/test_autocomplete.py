# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp.addons.mail.tests.common import TestMail

MAIL_TEMPLATE = """Return-Path: <whatever-2a840@postmaster.twitter.com>
To: {to}
Received: by mail1.openerp.com (Postfix, from userid 10002)
    id 5DF9ABFB2A; Fri, 10 Aug 2012 16:16:39 +0200 (CEST)
From: {email_from}
Subject: {subject}
MIME-Version: 1.0
Content-Type: multipart/alternative;
    boundary="----=_Part_4200734_24778174.1344608186754"
Date: Fri, 10 Aug 2012 14:16:26 +0000
Message-ID: {msg_id}
{extra}
------=_Part_4200734_24778174.1344608186754
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: quoted-printable

*** sale order number: {sale_number} ***

Please call me as soon as possible this afternoon!

--
Sylvie
------=_Part_4200734_24778174.1344608186754
Content-Type: text/html; charset=utf-8
Content-Transfer-Encoding: quoted-printable

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
 <head>=20
  <meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8" />
 </head>=20
 <body style=3D"margin: 0; padding: 0; background:
     #ffffff;-webkit-text-size-adjust: 100%;">=20

  *** sale order number: {sale_number} ***

  <p>Please call me as soon as possible this afternoon!</p>

  <p>--<br/>
     Sylvie
  <p>
 </body>
</html>
------=_Part_4200734_24778174.1344608186754--
"""


class TestMailAutocomplete(TestMail):

    @staticmethod
    def format(template, to='Claims <claims@example.com>',
               subject='1', extra='',
               email_from='Sylvie Lelitre <test.sylvie.lelitre@agrolait.com>',
               msg_id='',
               sale_number=''):
        return template.format(to=to, subject=subject, extra=extra,
                               email_from=email_from, msg_id=msg_id,
                               sale_number=sale_number)

    def setUp(self):
        super(TestMailAutocomplete, self).setUp()
        self.Claim = self.env['crm.claim']
        self.Sale = self.env['sale.order']
        self.SaleLine = self.env['sale.order.line']
        product = self.browse_ref('product.product_product_7')
        product.write({'invoice_policy': 'order'})
        partner = self.browse_ref('base.res_partner_4')
        partner.write({'email': 'loutres@qoqa.com'})

    def _create_sale_order(self, number):
        vals = {
            'name': number,
            'partner_id': self.ref('base.res_partner_3'),
        }

        line1 = {
            'product_id': self.ref('product.product_product_7'),
            'price_unit': 35.,
            'product_uom_qty': 10,
        }
        vals['order_line'] = [(0, 0, line1)]
        sale = self.Sale.create(vals)
        self.assertEqual(sale.name, number)
        return sale

    def _confirm_sale_order(self, sale):
        sale.action_confirm()
        self.assertEqual(sale.state, 'sale')

    def _create_invoice(self, sale):
        sale.action_invoice_create()
        self.assertTrue(sale.invoice_ids)

    def test_autocomplete(self):
        """ Autocomplete from sales / invoice """
        sale = self._create_sale_order('7531902')
        self._confirm_sale_order(sale)
        self._create_invoice(sale)
        invoice = sale.invoice_ids[0]

        company = self.env.user.company_id
        company.write({
            'claim_sale_order_regexp':
            u'\*\*\* sale order number: (\d+) \*\*\*'}
        )

        msg_id = '<6198923581.41972151344608186760.JavaMail.1@agrolait.com>'
        email = self.format(MAIL_TEMPLATE, msg_id=msg_id,
                            sale_number='7531902')
        # when processed, it should find the SO from the number, and
        # autocomplete the claim with the last invoice of the SO
        claim_id = self.Claim.message_process(self.Claim._name, email)
        claim = self.Claim.browse(claim_id)
        self.assertEqual(claim.invoice_id.id, invoice.id)
        self.assertEqual(len(claim.claim_line_ids), 1)
        lines = claim.claim_line_ids
        self.assertEqual(lines[0].product_id.id,
                         self.ref('product.product_product_7'))
        self.assertEqual(claim.partner_id.id, invoice.partner_id.id)
