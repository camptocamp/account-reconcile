# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp.osv import _, api, fields, models
from openerp.exceptions import UserError
from openerp import netsvc
#from openerp.tools.float_utils import float_round
#from openerp.addons.connector_qoqa.connector import get_environment
#from openerp.addons.connector.session import ConnectorSession
#from openerp.addons.connector.unit.backend_adapter import BackendAdapter


class CrmClaimUnclaimed(models.TransientModel):
    _name = 'crm.claim.unclaimed'

    @api.multi
    def _default_team_id(self):
        return self.env.ref('scenario.team_sale_team_livr')

    @api.multi
    def _default_user_id(self):
        team_id = self._default_team_id()
        team = self.env['crm.team'].browse(team_id)
        return team.user_id and team.user_id.id or False

    @api.multi
    def _default_categ_id(self):
        company = self.env.user.company_id
        return company.unclaimed_initial_categ_id and \
            company.unclaimed_initial_categ_id.id or False

    unclaimed_type = fields.Selection(
        [('invalid_address', 'Invalid Address'),
         ('unclaimed', 'Unclaimed')],
        default='unclaimed',
        required=True
    )
    track_number = fields.Char(
        string='Tracking Number',
        required=True
    )
    claim_name = fields.Char(
        string='Claim Subject',
        required=True
    )
    return_source_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Source Location',
        required=True
    )
    return_dest_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Dest. Location',
        required=True
    )
    claim_carrier_price = fields.Float(
        string='Delivery Carrier Price',
        required=True
    )
    claim_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        required=True
    )
    claim_sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        required=True
    )
    claim_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True
    )
    claim_delivery_address_id = fields.Many2one(
        comodel_name='res.partner',
        string='Delivery Address',
        required=True
    )
    claim_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=_default_user_id,
        required=True
    )
    claim_team_id = fields.Many2one(
        comodel_name='crm.team',
        string='Sales Team',
        default=_default_team_id,
        required=True
    )
    claim_categ_id = fields.Many2one(
        comodel_name='crm.case.categ',
        string='Category',
        default=_default_categ_id,
        required=True
    )

    @api.multi
    def _prepare_claim(self):
        """
            Method to fill claim with values from the wizard,
            onchanges (partner and invoice), and the corresponding
            template. Also calls the connector to get the URL
            from Datatrans.
        """
        self.ensure_one()
        claim_obj = self.env['crm.claim']

        # TODO after API is decided
        claim_number = claim_obj._get_sequence_number()
        sale = self.claim_sale_order_id
        pay_by_email_url = False
        #try:
        #    session = ConnectorSession()
        #    qsale = sale.qoqa_bind_ids[0]
        #    backend_id = qsale.backend_id.id
        #    env = get_environment(session, 'qoqa.sale.order', backend_id)
        #    adapter = env.get_connector_unit(BackendAdapter)
        #    amount = float_round(self.claim_carrier_price * 100,
        #                         precision_digits=0)
        #    pay_by_email_url = adapter.pay_by_email_url(
        #        qsale.qoqa_id, claim_number, int(amount))
        #    if not pay_by_email_url:
        #        raise
        #except:
        #    raise UserError(('Error'),
        #                    ('Pay by email not retrieved from BO!'))

        claim_vals = {
            'name': self.claim_name,
            'number': claim_number,
            'pay_by_email_url': pay_by_email_url,
            'user_id': self.claim_user_id.id,
            'team_id': self.claim_team_id.id,
            'claim_type': 'customer',
            'categ_id': self.claim_categ_id.id,
            'ref': 'sale.order,%s' % sale.id,
            'partner_id': self.claim_partner_id.id,
            'invoice_id': self.claim_invoice_id.id,
            'unclaimed_price': int(self.claim_carrier_price)
        }

        # Call on_change functions to retrieve values
        on_change_partner_vals = claim_obj.onchange_partner_id(
            self.claim_partner_id.id)
        claim_vals.update(on_change_partner_vals['value'])

        on_change_invoice_vals = claim_obj.onchange_invoice_id(
            invoice_id=self.claim_invoice_id.id,
            warehouse_id=False, claim_type='customer',
            claim_date=fields.Datetime.now(),
            company_id=sale.company_id.id,
            lines=False, create_lines=True)
        claim_vals.update(on_change_invoice_vals['value'])
        # store correctly claim lines
        if 'claim_line_ids' in claim_vals:
            # Set all lines with the same destination
            claim_lines = claim_vals['claim_line_ids']
            for claim_line in claim_lines:
                claim_line.update({
                    'warranty_type': 'company',
                    'warranty_return_partner': sale.company_id.partner_id.id,
                    'location_dest_id': self.return_dest_location_id.id
                })
            claim_vals['claim_line_ids'] = \
                [(0, 0, line) for line in claim_lines]

        # Set correct delivery address (retrieved from picking)
        claim_vals.update({
            'delivery_address_id': self.claim_delivery_address_id.id
        })

        # Set correct mail template
        if self.unclaimed_type == 'unclaimed':
            template_id = self.env.ref(
                'crm_claim_mail.email_template_rma_unclaimed')
        elif self.unclaimed_type == 'invalid_address':
            template_id = self.env.ref(
                'crm_claim_mail.email_template_rma_invalid_address')

        claim_vals.update({
            'confirmation_email_sent': False,
            'confirmation_email_template': template_id
        })

        return claim_vals

    @api.multi
    def _call_return_wizard(self, claim):
        """
            Call to product_return wizard
        """
        picking_obj = self.env['stock.picking']
        return_wiz_obj = self.env['claim_make_picking.wizard']
        company = self.env.user.company_id
        # Create refund from claim
        ctx = {
            'active_id': claim.id,
            'warehouse_id': claim.warehouse_id.id,
            'partner_id': claim.partner_id.id,
            'picking_type': 'in',
            'product_return': True
        }
        return_wiz = return_wiz_obj.with_context(ctx).create(
            {'claim_line_source_location':
                self.return_source_location_id.id,
                'claim_line_dest_location':
                self.return_dest_location_id.id
             })
        wiz_result = return_wiz.action_create_picking()
        picking = picking_obj.with_context(ctx).browse(wiz_result['res_id'])
        # Set stock journal on newly created picking
        if company.unclaimed_stock_journal_id:
            journal_id = company.unclaimed_stock_journal_id.id
            picking.write({'stock_journal_id': journal_id})
        # Set picking as done
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(self.env.user, 'stock.picking', picking.id,
                                'button_done', self.env.cr)
        return wiz_result

    @api.multi
    @api.depends('track_number')
    def onchange_package_number(self):
        """
            Onchange to set all values (or return errors)
            from the tracking number
        """
        res = {'value': {'claim_name': False,
                         'return_source_location_id': False,
                         'return_dest_location_id': False,
                         'claim_invoice_id': False,
                         'claim_sale_order_id': False,
                         'claim_partner_id': False,
                         'claim_delivery_address_id': False,
                         'claim_carrier_price': False}}
        track_obj = self.env['stock.tracking']
        if not self.track_number:
            return res

        track_ids = track_obj.search([('serial', '=', self.track_number)])
        if not track_ids:
            raise UserError(_('Error'),
                            _('Not a valid tracking number!'))
        move = track_ids[0].move_ids and track_ids[0].move_ids[0] or False
        if not move:
            raise UserError(
                _('Error'),
                _('No stock move associated to this tracking number!')
            )
        res['value'].update({
            'return_source_location_id': move.location_dest_id.id
        })

        carrier = move.picking_id and move.picking_id.carrier_id
        if not carrier:
            raise UserError(
                _('Error'),
                _('No delivery carrier associated to this tracking number!')
            )
        carrier_price = carrier.normal_price
        if not carrier_price:
            raise UserError(
                _('Error'),
                _('No price set on delivery carrier %s!') % (carrier.name, )
            )
        res['value'].update({
            'claim_delivery_address_id': move.picking_id.partner_id.id,
            'claim_carrier_price': carrier_price,
        })

        sale = move.sale_line_id and move.sale_line_id.order_id or False
        if not sale:
            raise UserError(
                _('Error'),
                _('No sale associated to this tracking number!')
            )
        invoice = sale.invoice_ids and sale.invoice_ids[0] or False
        if not invoice:
            raise UserError(
                _('Error'),
                _('No invoice associated to this tracking number!')
            )
        if sale.partner_id and sale.partner_id.lang == 'de_DE':
            claim_name = _('Ihre Bestellung Nr. %s') % (sale.name, )
        else:
            claim_name = _('Votre commande numéro %s en retour non-réclamé') \
                % (sale.name, )
        res['value'].update({
            'claim_name': claim_name,
            'claim_invoice_id': invoice.id,
            'claim_sale_order_id': sale.id,
            'claim_partner_id': sale.partner_id.id
        })
        return res

    @api.multi
    def create_claim(self, cr, uid, ids, context=None):
        # Function to create claim and return with given parameters
        self.ensure_one()
        claim_obj = self.env['crm.claim']
        claim_vals = self._prepare_claim()
        # Create and resolve claim
        claim = claim_obj.create(claim_vals)
        claim.case_close()
        # Create refund from claim
        return self._call_return_wizard(claim)
