# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA (Joël Grandguillaume, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import re
from openerp import _, api, fields, models
from openerp.tools import html2plaintext


class CrmClaimStage(models.Model):
    """ re-add states (to know which to
        use for cancel/close/draft/pending) """
    _inherit = "crm.claim.stage"

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'In Progress'),
        ('done', 'Closed'),
        ('cancel', 'Cancelled')],
        string="State")


class CrmTeam(models.Model):
    """ Category of Case """
    _inherit = "crm.team"

    notify = fields.Boolean('Notify on change')


class CrmClaim(models.Model):
    """ Crm claim
    """
    _inherit = "crm.claim"

    priority = fields.Selection(
        [('0', 'Low'),
         ('1', 'Normal'),
         ('2', 'High')],
        string='Customer Satisfaction')

    company_id = fields.Many2one(
        related='warehouse_id.company_id',
        comodel_name='res.company',
        string='Company',
        store=True,
        readonly=True
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        domain=['|', ('active', '=', False), ('active', '=', True)],
        help='Related original Customer invoice'
    )
    partner_street = fields.Char(
        related='partner_id.street',
        string='Partner Street',
        store=True,
        readonly=True
    )
    partner_zip = fields.Char(
        related='partner_id.zip',
        string='Partner ZIP code',
        store=True,
        readonly=True
    )
    partner_city = fields.Char(
        related='partner_id.city',
        string='Partner City',
        store=True,
        readonly=True
    )

    description = fields.Html('Description')
    plain_text_description = fields.Text('Description in text form',
                                         compute='_get_plain_text_description')

    @api.depends('description')
    def _get_plain_text_description(self):
        for claim in self:
            desc = html2plaintext(claim.description)
            claim.plain_text_description = re.sub(r'(\n){3,}', '\n\n', desc)

    @api.multi
    def notify_user(self, partner_id):
        for claim in self:
            body = _('A new CRM claim (%s) has been assigned to you'
                     % (claim.name))
            subject = _('A new CRM claim has been assigned to you')
            claim.message_post(body=body, subject=subject,
                               message_type='email',
                               subtype='mail.mt_comment',
                               parent_id=False,
                               attachments=None,
                               partner_ids=[partner_id])

    @api.multi
    def notify_claim_only_specific_user(self, partner_id):
        for claim in self:
            # Get all followers of current claim
            partner_ids = claim.message_partner_ids.ids
            channel_ids = claim.message_channel_ids.ids
            if partner_ids or channel_ids:
                    # Remove followers on the message
                    # to not send an unuseful message to the related customer
                    claim.message_unsubscribe(partner_ids, channel_ids)
            claim.notify_user(partner_id)
            if partner_ids or channel_ids:
                # Resuscribe all partner include customer
                claim.message_subscribe(partner_ids, channel_ids)

    @api.model
    def create(self, vals):
        claim = super(CrmClaim, self).create(vals)
        if vals.get('user_id'):
            # If a user is selected we remove all previous selected
            # partners
            fol_obj = self.env['mail.followers']
            followers = fol_obj.search([('res_model', '=', self._name),
                                        ('res_id', '=', claim.id)])
            old = [fol.partner_id.id for fol in followers]
            claim.message_unsubscribe(old)
            user_obj = self.env['res.users']
            responsible = user_obj.browse(vals['user_id'])
            claim.message_subscribe([responsible.partner_id.id])
            if vals.get('team_id'):
                team_obj = self.env['crm.team']
                team = team_obj.browse(vals['team_id'])
                if team.notify:
                    claim.notify_user(responsible.partner_id.id)
        if vals.get('partner_id'):
            claim.message_subscribe([vals['partner_id']])
        return claim

    @api.multi
    def write(self, vals):
        for claim in self:
            # Remove previous partner
            if vals.get('partner_id'):
                # If the partner selected differ from the partner
                # previously selected:
                if claim.partner_id:
                    if claim.partner_id.id != vals['partner_id']:
                        claim.message_unsubscribe([claim.partner_id.id])
                # We subcribe the sected partner to it
                claim.message_subscribe([vals['partner_id']])

            # Make the same for the Responsible (user_id):
            responsible = False
            if vals.get('user_id'):
                user_obj = self.env['res.users']
                responsible = user_obj.browse(vals['user_id'])
                # If the partner selected differ from the partner
                # previously selected:
                if claim.user_id:
                    if claim.user_id.id != vals['user_id']:
                        claim.message_unsubscribe(
                            [claim.user_id.partner_id.id])
                # We subcribe the selected partner to it
                claim.message_subscribe([responsible.partner_id.id])

            team = None
            if vals.get('team_id'):
                team_obj = self.env['crm.team']
                team = team_obj.browse(vals['team_id'])
            # Notification parts
            # We only check notification if section or responsible is modified
            if team or responsible:
                # fill team and responsible information
                if team:
                    current_team = team
                else:
                    current_team = claim.team_id
                if responsible:
                    current_responsible = responsible
                else:
                    current_responsible = claim.user_id
                # Check if the section need to be notify
                if current_team.notify:
                    notify_partner_id = current_responsible.partner_id.id
                    if notify_partner_id:
                        claim.notify_claim_only_specific_user(
                            notify_partner_id
                        )

        return super(CrmClaim, self).write(vals)

    """
        Methods to set claims to specific stages
    """
    @api.multi
    def case_close(self):
        """ Mark the claim as closed: state=done """
        for claim in self:
            stage_id = claim.stage_find([], claim.team_id.id,
                                        [('state', '=', 'done')])
            if stage_id:
                claim.stage_id = stage_id


class ClaimLine(models.Model):
    """ Crm claim
    """
    _inherit = "claim.line"

    return_instruction = fields.Many2one(
        'return.instruction',
        'Instructions',
        compute='_compute_return_instruction',
        help="Instructions for product return"
    )

    @api.multi
    def _compute_return_instruction(self):
        for line in self:
            if line.product_id and line.product_id.seller_ids:
                supplier = line.product_id.seller_ids[0]
                line.return_instruction = supplier.return_instructions

    @api.model
    def create(self, vals):
        result = super(ClaimLine, self).create(vals)
        result.auto_set_warranty()
        return result
