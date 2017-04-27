# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields


class QoqaShop(models.Model):
    _inherit = 'qoqa.shop'

    mail_signature_template = fields.Text(
        string='Mail signature template',
        required=True,
        translate=True,
        help='This is the mail signature template. You can add some'
        ' variables :\n'
        '$user_signature : the current user signature\n'
        '$user_email : the current user email'
    )
