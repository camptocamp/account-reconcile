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


class TestMailAutocomplete(TestMailBase):

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
        self.Claim = self.registry('crm.claim')
        self.Sale = self.registry('sale.order')
        self.SaleLine = self.registry('sale.order.line')

    def _create_sale_order(self, number):
        cr, uid = self.cr, self.uid
        vals = {
            'name': number,
            'partner_id': self.ref('base.res_partner_3'),
            'shop_id': self.ref('sale.sale_shop_1'),
        }
        vals.update(
            self.Sale.onchange_shop_id(cr, uid, [], vals['shop_id'])['value']
        )
        vals.update(
            self.Sale.onchange_partner_id(cr, uid, [],
                                          vals['partner_id'])['value']
        )

        line1 = {
            'product_id': self.ref('product.product_product_7'),
            'price_unit': 35.,
            'product_uom_qty': 10,
        }
        line1.update(
            self.SaleLine.product_id_change(
                cr, uid, [], vals['pricelist_id'],
                line1['product_id'],
                qty=line1['product_uom_qty'],
                partner_id=vals['partner_id'])['value']
        )
        vals['order_line'] = [(0, 0, line1)]
        sale_id = self.Sale.create(cr, uid, vals)
        sale = self.Sale.browse(cr, uid, sale_id)
        self.assertEqual(sale.name, number)
        return sale_id

    def _confirm_sale_order(self, sale_id):
        cr, uid = self.cr, self.uid
        self.Sale.action_button_confirm(cr, uid, [sale_id])
        sale = self.Sale.browse(cr, uid, sale_id)
        self.assertEqual(sale.state, 'manual')

    def _create_invoice(self, sale_id):
        cr, uid = self.cr, self.uid
        self.Sale.action_invoice_create(cr, uid, [sale_id])
        sale = self.Sale.browse(cr, uid, sale_id)
        self.assertTrue(sale.invoice_ids)

    def test_autocomplete(self):
        """ Autocomplete from sales / invoice """
        cr, uid = self.cr, self.uid
        sale_id = self._create_sale_order('7531902')
        self._confirm_sale_order(sale_id)
        self._create_invoice(sale_id)
        sale = self.Sale.browse(cr, uid, sale_id)
        invoice = sale.invoice_ids[0]

        User = self.registry('res.users')
        company = User.browse(cr, uid, uid).company_id
        company.write({
            'claim_sale_order_regexp':
            u'\*\*\* sale order number: (\d+) \*\*\*'}
        )

        msg_id = '<6198923581.41972151344608186760.JavaMail.1@agrolait.com>'
        email = self.format(MAIL_TEMPLATE, msg_id=msg_id,
                            sale_number='7531902')
        # when processed, it should find the SO from the number, and
        # autocomplete the claim with the last invoice of the SO
        claim_id = self.Claim.message_process(cr, uid, self.Claim._name, email)
        claim = self.Claim.browse(cr, uid, claim_id)
        self.assertEqual(claim.invoice_id.id, invoice.id)
        self.assertEqual(len(claim.claim_line_ids), 1)
        lines = claim.claim_line_ids
        self.assertEqual(lines[0].product_id.id,
                         self.ref('product.product_product_7'))
        self.assertEqual(claim.partner_id.id, invoice.partner_id.id)
