# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import api, fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    qoqa_team_id = fields.Many2one(
        string="Team QoQa",
        comodel_name="qoqa.team",
    )
    color = fields.Integer(
        string="Color Index",
    )
    non_assigned_claims_qty = fields.Integer(
        string="Non-assigned Claims",
        compute="_compute_non_assigned_claims_qty",
    )
    notify = fields.Boolean(
        string='Notify on change',
    )
    claim_ids = fields.One2many(
        string="Claims",
        comodel_name="crm.claim",
        inverse_name="team_id",
        copy=False,
    )
    new_claims_qty = fields.Integer(
        string="New Claims",
        compute="_compute_claims_by_stages_qty",
    )
    response_received_claims_qty = fields.Integer(
        string="Response Received Claims",
        compute="_compute_claims_by_stages_qty",
    )
    in_progress_claims_qty = fields.Integer(
        string="In Progress Claims",
        compute="_compute_claims_by_stages_qty",
    )
    settled_claims_qty = fields.Integer(
        string="Settled Claims",
        compute="_compute_claims_by_stages_qty",
    )

    @api.depends('claim_ids', 'claim_ids.stage_id')
    def _compute_claims_by_stages_qty(self):
        stages = {
            "new": self.env.ref("crm_claim.stage_claim1"),
            "responce": self.env.ref("qoqa_claim.stage_response_received"),
            "progress": self.env.ref("crm_claim.stage_claim5"),
            "settled": self.env.ref("crm_claim.stage_claim2"),
        }
        for record in self:
            record.new_claims_qty = len(record.claim_ids.filtered(
                lambda x: x.stage_id == stages["new"]
            ))
            record.response_received_claims_qty = len(
                record.claim_ids.filtered(
                    lambda x: x.stage_id == stages["responce"]
                )
            )
            record.in_progress_claims_qty = len(record.claim_ids.filtered(
                lambda x: x.stage_id == stages["progress"]
            ))
            record.settled_claims_qty = len(record.claim_ids.filtered(
                lambda x: x.stage_id == stages["settled"]
            ))

    @api.depends('claim_ids', 'claim_ids.user_id')
    def _compute_non_assigned_claims_qty(self):
        for record in self:
            record.non_assigned_claims_qty = len(record.claim_ids.filtered(
                lambda x: not x.user_id
            ))

    @api.multi
    def get_unassigned_claims_action(self):
        self.ensure_one()
        action = self.env.ref("qoqa_claim.act_crm_claim_rma_claim").read()[0]
        action["domain"] = [
            ('team_id', '=', self.id),
            ('user_id', '=', False),
        ]
        action["context"] = {'search_default_group_categ_id': 1}
        return action

    @api.multi
    def get_new_claims_action(self):
        self.ensure_one()
        action = self.env.ref("qoqa_claim.act_crm_claim_rma_claim").read()[0]
        action["domain"] = [
            ('team_id', '=', self.id),
            ('stage_id', '=', self.env.ref("crm_claim.stage_claim1").id),
        ]
        action["context"] = {
            'search_default_group_categ_id': 1,
            'search_default_group_user_id': 1,
        }
        return action

    @api.multi
    def get_response_recieved_claims_action(self):
        self.ensure_one()
        action = self.env.ref("qoqa_claim.act_crm_claim_rma_claim").read()[0]
        action["domain"] = [
            ('team_id', '=', self.id),
            ('stage_id', '=', self.env.ref(
                "qoqa_claim.stage_response_received"
            ).id),
        ]
        action["context"] = {
            'search_default_group_categ_id': 1,
            'search_default_group_user_id': 1,
        }
        return action

    @api.multi
    def get_in_progress_claims_action(self):
        self.ensure_one()
        action = self.env.ref("qoqa_claim.act_crm_claim_rma_claim").read()[0]
        action["domain"] = [
            ('team_id', '=', self.id),
            ('stage_id', '=', self.env.ref("crm_claim.stage_claim5").id),
        ]
        action["context"] = {
            'search_default_group_categ_id': 1,
            'search_default_group_user_id': 1,
        }
        return action

    @api.multi
    def get_settled_claims_action(self):
        self.ensure_one()
        action = self.env.ref("qoqa_claim.act_crm_claim_rma_claim").read()[0]
        action["domain"] = [
            ('team_id', '=', self.id),
            ('stage_id', '=', self.env.ref("crm_claim.stage_claim2").id),
        ]
        action["context"] = {
            'search_default_group_categ_id': 1,
            'search_default_group_user_id': 1,
        }
        return action

    @api.multi
    def get_all_claims_action(self):
        self.ensure_one()
        action = self.env.ref("qoqa_claim.act_crm_claim_rma_claim").read()[0]
        action["domain"] = [
            ('team_id', '=', self.id),
        ]
        return action
