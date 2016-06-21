# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import api, models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.multi
    def get_needaction_data(self):
        """ Disable all counters for menus, for performance
        """
        return dict.fromkeys(self.ids, {
            'needaction_enabled': False,
            'needaction_counter': False,
        })
