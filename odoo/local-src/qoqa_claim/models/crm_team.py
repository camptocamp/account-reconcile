# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    qoqa_team_id = fields.Many2one(
        string="Team QoQa",
        comodel_name="qoqa.team",
    )

    notify = fields.Boolean('Notify on change')
