# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    journal_id = fields.Many2one(index=True)

    def init(self, cr):
        # index for the default _order of account.move
        index_name = 'account_move_order_list_sort_index'
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s',
                   (index_name,))

        if not cr.fetchone():
            cr.execute('CREATE INDEX %s ON account_move '
                       '(date DESC, id DESC) ' % index_name)
