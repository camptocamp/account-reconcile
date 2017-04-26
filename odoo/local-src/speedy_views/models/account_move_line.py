# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models
from .utils import create_index


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Override _order set in account_move_base_import and which is
    # slow as hell. We redefine the original one.
    _order = 'date DESC, id DESC'

    def init(self, cr):

        # in reconcile wizard, queries look for null or false values
        # for 'reconciled'. We improve the mass reconciliations with
        # this partial index
        index_name = 'account_move_line_not_reconciled_index'
        create_index(cr, index_name, self._table,
                     '(reconciled) WHERE '
                     'reconciled IS NULL OR NOT reconciled ')
