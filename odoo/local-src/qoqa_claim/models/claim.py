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
    partner_category_ids = fields.Many2many(
        string="Partner tags",
        related="partner_id.category_id"
    )

    description = fields.Html('Description')
    plain_text_description = fields.Text('Description in text form',
                                         compute='_get_plain_text_description')

    sale_order_count = fields.Integer(
        related="partner_id.sale_order_count"
    )
    claim_count = fields.Integer(
        related='partner_id.claim_count',
    )

    # Add domain based on sales team
    categ_id = fields.Many2one(
        domain="[('team_id', '=', team_id)]",
    )

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
            # Add variable to context so that we know not to change the status
            msg = claim.message_post(
                body=body,
                subject=subject,
                message_type='email',
                subtype='mail.mt_comment',
                parent_id=False,
                attachments=None,
                partner_ids=[partner_id]
            )
            # Delete after sending e-mail to avoid quoting it later on
            msg.unlink()

    @api.constrains('user_id', 'team_id')
    def notify_claim_only_specific_user(self):
        """Manage user notification
        tweaked usage of constraint as a post write hook.
        We have to do this as a this function remove a message.
        Because of the way mail thread reimplement the security
        check and the MRO of chanined inherits we try
        to read the id of the deleted message leading to
        an acces error
        """
        for claim in self:
            partner_id = claim.user_id.partner_id
            if not all([claim.team_id.notify, partner_id]):
                continue
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

    warranty_return_address = fields.Many2one(
        'res.partner',
        compute='_compute_warranty_values',
        help="Warranty return address of the product")

    return_instruction = fields.Many2one(
        'return.instruction',
        'Instructions',
        compute='_compute_warranty_values',
        help="Instructions for product return"
    )

    return_instruction_name = fields.Char(
        'Instructions Title',
        compute='_compute_warranty_values',
        help="Instructions title for product return"
    )
    return_instruction_details = fields.Text(
        'Instructions details',
        compute='_compute_warranty_values',
        help="Instructions details for product return"
    )

    @api.multi
    def _compute_warranty_values(self):
        for line in self:
            supplier_infos = line.product_id.seller_ids
            if supplier_infos:
                address = supplier_infos[0].warranty_return_address
                instructions = supplier_infos[0].return_instructions
                line.warranty_return_address = address
                line.return_instruction = instructions
                line.return_instruction_name = instructions.name
                line.return_instruction_details = instructions.instructions

    @api.model
    def create(self, vals):
        result = super(ClaimLine, self).create(vals)
        result.auto_set_warranty()
        return result
