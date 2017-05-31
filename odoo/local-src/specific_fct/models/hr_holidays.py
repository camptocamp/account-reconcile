# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, models


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def message_post(self, body='', subject=None, message_type='notification',
                     subtype=None, parent_id=False, attachments=None,
                     content_subtype='html', **kwargs):
        # De-activate all outgoing mails for holidays
        return True
