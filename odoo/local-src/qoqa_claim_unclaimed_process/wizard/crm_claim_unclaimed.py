# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import time
from openerp import _, api, fields, models
from openerp.exceptions import UserError
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.unit.backend_adapter import BackendAdapter
from openerp.addons.connector.connector import Binder

from openerp.addons.connector_qoqa.connector import get_environment
from openerp.addons.connector_qoqa.unit.backend_adapter import (
    api_handle_errors,
)


class CrmClaimUnclaimed(models.TransientModel):
    _name = 'crm.claim.unclaimed'

    @api.multi
    def _default_team_id(self):
        return self.env.ref('scenario.section_sale_team_livr')

    @api.multi
    def _default_user_id(self):
        team = self._default_team_id()
        return team.user_id

    @api.multi
    def _default_categ_id(self):
        company = self.env.user.company_id
        return company.unclaimed_initial_categ_id or \
            self.env['crm.claim.category']

    unclaimed_type = fields.Selection(
        [('invalid_address', 'Invalid Address'),
         ('unclaimed', 'Unclaimed')],
        default='unclaimed',
    )
    track_number = fields.Char(
        string='Tracking Number',
    )
    claim_name = fields.Char(
        string='Claim Subject',
    )
    return_source_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Source Location',
    )
    return_dest_location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Dest. Location',
    )
    claim_carrier_price = fields.Float(
        string='Delivery Carrier Price',
    )
    claim_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
    )
    claim_package_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Unclaimed Package',
    )
    claim_sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
    )
    claim_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
    )
    claim_delivery_address_id = fields.Many2one(
        comodel_name='res.partner',
        string='Delivery Address',
    )
    claim_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        default=_default_user_id,
    )
    claim_team_id = fields.Many2one(
        comodel_name='crm.team',
        string='Sales Team',
        default=_default_team_id,
    )
    claim_categ_id = fields.Many2one(
        comodel_name='crm.claim.category',
        string='Category',
        default=_default_categ_id,
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
        customer_type = self.env.ref('crm_claim_type.crm_claim_type_customer')

        claim_number = claim_obj._get_sequence_number(customer_type.id)
        sale = self.claim_sale_order_id
        pay_by_email_url = False

        qsale = sale.qoqa_bind_ids
        backend = qsale.backend_id

        if not self.claim_carrier_price:
            raise UserError(
                _('The carrier has no fixed price.')
            )

        session = ConnectorSession.from_env(self.env)
        with get_environment(session, 'qoqa.sale.order',
                             backend.id) as connector_env:
            msg = ('"Pay by email" URL could not be obtained on the BO, '
                   'try later')
            sale_adapter = connector_env.get_connector_unit(BackendAdapter)
            binder = connector_env.get_connector_unit(Binder)
            with api_handle_errors(message=msg):
                payment = sale_adapter.create_payment(
                    binder.to_backend(qsale),
                    self.claim_carrier_price,
                    'unclaimed',
                    claim_number
                )
                payment_id = payment['data']['id']

        # We have to poll the GET method until we have a value in 'payment_url'
        # because the payment is created on Datatrans by a job on the Backend's
        # side. Once the timeout is reached, we just raise an error and the
        # user has to retry later
        with get_environment(session, 'qoqa.payment',
                             backend.id) as connector_env:
            payment_adapter = connector_env.get_connector_unit(BackendAdapter)
            payment = payment_adapter.read(payment_id)
            pay_by_email_url = payment['data']['attributes'].get('payment_url')
            retries = 0
            while retries < 10 and not pay_by_email_url:
                time.sleep(2)
                payment = payment_adapter.read(payment_id)
                attributes = payment['data']['attributes']
                pay_by_email_url = attributes.get('payment_url')
                retries += 1
            if not pay_by_email_url:
                raise UserError(
                    _('The payment could not be created on the BO. '
                      'Retry later.')
                )

        claim_vals = {
            'name': self.claim_name,
            'code': claim_number,
            'pay_by_email_url': pay_by_email_url,
            'user_id': self.claim_user_id.id,
            'team_id': self.claim_team_id.id,
            'claim_type': customer_type.id,
            'categ_id': self.claim_categ_id.id,
            'ref': 'sale.order,%s' % sale.id,
            'partner_id': self.claim_partner_id.id,
            'invoice_id': self.claim_invoice_id.id,
            'qoqa_shop_id': self.claim_sale_order_id.qoqa_shop_id.id,
            'unclaimed_price': int(self.claim_carrier_price),
            'unclaimed_package_id': self.claim_package_id.id
        }
        # Call on_change functions to retrieve values
        on_change_partner_vals = claim_obj.onchange_partner_id(
            self.claim_partner_id.id)
        claim_vals.update(on_change_partner_vals['value'])

        # Create memory object to use other on_change
        temp_claim = claim_obj.with_context(create_lines=True).new(claim_vals)
        temp_claim._onchange_invoice_warehouse_type_date()
        # Add values to claim lines
        for claim_line in temp_claim.claim_line_ids:
            claim_line.warning = 'not_define'
            claim_line.warranty_type = 'company'
            claim_line.warranty_return_partner = sale.company_id.partner_id.id
            claim_line.location_dest_id = self.return_dest_location_id.id
        claim_vals = temp_claim._convert_to_write(temp_claim._cache)

        # Set correct delivery address (retrieved from picking)
        claim_vals.update({
            'delivery_address_id': self.claim_delivery_address_id.id
        })

        # Set correct mail template
        if self.unclaimed_type == 'unclaimed':
            template = self.env.ref(
                'qoqa_claim_unclaimed_process.email_template_rma_unclaimed')
        elif self.unclaimed_type == 'invalid_address':
            template = self.env.ref(
                'qoqa_claim_unclaimed_process.'
                'email_template_rma_invalid_address')

        claim_vals.update({
            'confirmation_email_sent': False,
            'confirmation_email_template': template.id
        })

        return claim_vals

    @api.multi
    def _call_return_wizard(self, claim):
        """
            Call to product_return wizard
        """
        return_wiz_obj = self.env['claim_make_picking.wizard']
        valid_wiz_obj = self.env['stock.immediate.transfer']
        # Create refund from claim
        ctx = {
            'active_id': claim.id,
            'warehouse_id': claim.warehouse_id.id,
            'partner_id': claim.partner_id.id,
            'picking_type': 'in',
            'product_return': True
        }
        return_wiz = return_wiz_obj.with_context(ctx).create(
            {'claim_line_source_location_id':
             self.return_source_location_id.id,
             'claim_line_dest_location_id':
             self.return_dest_location_id.id
             })
        wiz_result = return_wiz.action_create_picking()
        wiz_valid = valid_wiz_obj.create({'pick_id': wiz_result['res_id']})
        wiz_valid.process()
        return wiz_result

    @api.onchange('track_number')
    def onchange_package_number(self):
        """
            Onchange to set all values (or return errors)
            from the tracking number
        """
        self.ensure_one()
        self.claim_package_id = False
        self.claim_name = False
        self.return_source_location_id = False
        self.return_dest_location_id = False
        self.claim_invoice_id = False
        self.claim_sale_order_id = False
        self.claim_partner_id = False
        self.claim_delivery_address_id = False
        self.claim_carrier_price = False
        pack_model = self.env['stock.quant.package']
        pack_operation_model = self.env['stock.pack.operation']
        if not self.track_number:
            return

        pack = pack_model.search(
            [('parcel_tracking', '=', self.track_number)],
            limit=1,
        )
        if not pack:
            raise UserError(_('Not a valid tracking number!'))

        self.claim_package_id = pack.id
        pack_op = pack_operation_model.search(
            [('result_package_id', '=', pack.id)],
            limit=1,
        )
        picking = pack_op.picking_id
        if not picking:
            raise UserError(_('Delivery order not found '
                              'for this tracking number!'))

        self.return_source_location_id = picking.location_dest_id.id
        self.claim_delivery_address_id = picking.partner_id.id
        self.claim_carrier_price = picking.carrier_id.fixed_price

        sale = picking.sale_id
        if not sale:
            raise UserError(
                _('No sale associated to this tracking number!')
            )
        invoice = sale.invoice_ids and sale.invoice_ids[0] or False
        if not invoice:
            raise UserError(
                _('No invoice associated to this tracking number!')
            )
        if sale.partner_id and sale.partner_id.lang == 'de_DE':
            claim_name = _('Ihre Bestellung Nr. %s') % (sale.name, )
        else:
            claim_name = _('Votre commande numéro %s en '
                           'retour non-réclamé') % (sale.name, )
        self.claim_name = claim_name
        self.claim_invoice_id = invoice.id
        self.claim_sale_order_id = sale.id
        self.claim_partner_id = sale.partner_id.id

    @api.multi
    def create_claim(self):
        if not all([
                self.track_number,
                self.unclaimed_type,
                self.claim_name,
                self.return_source_location_id,
                self.return_dest_location_id,
                self.claim_invoice_id,
                self.claim_sale_order_id,
                self.claim_carrier_price,
                self.claim_delivery_address_id,
                self.claim_partner_id,
                self.claim_user_id,
                self.claim_team_id,
                self.claim_categ_id,
                self.claim_package_id,
        ]):
            raise UserError(_(
                "Not all fields are filled!"
            ))
        # Function to create claim and return with given parameters
        self.ensure_one()
        claim_obj = self.env['crm.claim']
        claim_vals = self._prepare_claim()
        # Create and resolve claim
        claim = claim_obj.create(claim_vals)
        claim.case_close()
        # Create refund from claim
        return self._call_return_wizard(claim)
