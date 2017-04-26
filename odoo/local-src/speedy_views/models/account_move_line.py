# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Override _order set in account_move_base_import and which is
    # slow as hell. We redefine the original one.
    _order = 'date DESC, id DESC'
