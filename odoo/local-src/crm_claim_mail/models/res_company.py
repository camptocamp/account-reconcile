# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    claim_sale_order_regexp = fields.Char(
        string='Regular Expression for sale number',
        default=(u'<b>Order :</b>\s*<a '
                 'href="http[^"]+"[^>]*>(\d+)</a>'),
        help="Regular expression used to extract the sales order's "
        "number from the body of the emails."
    )
    mail_signature_template = fields.Html(
        string='Mail signature template',
        required=True,
        translate=True,
        default=(u'<p>Best wishes</p>'),
        help='This is the mail signature template. You can add some'
        ' variables :'
        '$user_signature : the current user signature'
        '$user_email : the current user email'
    )
