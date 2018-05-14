# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA (Joël Grandguillaume, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import re
from openerp import api, fields, models
from openerp.tools import html2plaintext


class CrmClaimCategory(models.Model):
    _inherit = 'crm.claim.category'

    active = fields.Boolean(
        string='Active',
        default=True,
        help="The active field allows you to hide the record without "
             "removing it."
    )


class CrmClaimStage(models.Model):
    """ re-add states (to know which to
        use for cancel/close/draft/pending) """
    _inherit = "crm.claim.stage"

    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'In Progress'),
        ('done', 'Closed'),
        ('cancel', 'Cancelled')
    ], string="State")


class CrmClaim(models.Model):
    """ Crm claim
    """
    _inherit = "crm.claim"

    qoqa_team_id = fields.Many2one(
        related="team_id.qoqa_team_id",
        readonly=True,
        store=True,
    )
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

    # Used to search per return products
    product_id = fields.Many2one(
        'product.product',
        related='claim_line_ids.product_id',
        string='Product')

    # Add domain based on sales team
    categ_id = fields.Many2one(
        domain="[('team_id', '=', team_id)]",
    )

    # field for attrs on view form of button assign
    is_user_current = fields.Boolean(compute='_compute_is_user_current')

    @api.multi
    def _compute_is_user_current(self):
        for rec in self:
            self.is_user_current = self.user_id == self.env.user

    @api.depends('description')
    def _get_plain_text_description(self):
        for claim in self:
            desc = html2plaintext(claim.description)
            claim.plain_text_description = re.sub(r'(\n){3,}', '\n\n', desc)

    def notify_claim_only_specific_user(self):
        for claim in self:

            mail_template = self.env.ref(
                'qoqa_claim.mail_template_crm_claim_change_user'
            )
            if mail_template:
                # Get all followers of current claim
                partner_ids = claim.message_partner_ids.ids
                channel_ids = claim.message_channel_ids.ids
                if partner_ids or channel_ids:
                    # Remove followers on the message
                    # to not send an unuseful message to the related customer
                    claim.message_unsubscribe(partner_ids, channel_ids)

                base_url = self.env['ir.config_parameter'].get_param(
                    'web.base.url')

                message = self.env['mail.compose.message'].with_context(
                    base_url=base_url,
                    no_case_close=True,
                ).create({
                    'model': 'crm.claim',
                    'res_id': claim.id,
                    'partner_ids': claim.user_id.partner_id.ids,
                    'template_id': mail_template.id,
                })
                message.onchange_template_id_wrapper()
                message.send_mail_action()

                if partner_ids or channel_ids:
                    # Resuscribe all partner include customer
                    claim.message_subscribe(partner_ids, channel_ids)

    @api.multi
    def assign_current_user(self):
        self.update({'user_id': self.env.uid})

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
        result = super(CrmClaim, self).write(vals)
        if vals.get('user_id'):
            self.notify_claim_only_specific_user()
        return result

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
