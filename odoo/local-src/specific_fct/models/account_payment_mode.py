# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    refund_max_days = fields.Integer('Refund max days',
                                     help="Number of days when the "
                                     "refund is possible")
    refund_min_date = fields.Date('Refund min date',
                                  help="Invoice date older than "
                                  "this value cannot be refund")
