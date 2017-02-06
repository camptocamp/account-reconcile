# -*- coding: utf-8 -*-
# © 2014-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _order = 'date desc, already_completed desc'
