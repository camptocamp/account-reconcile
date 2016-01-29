# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class crm_claim(orm.Model):
    """ Crm claim
    """
    _inherit = "crm.claim"

    _columns = {
        'company_id': fields.related(
            'warehouse_id',
            'company_id',
            type='many2one',
            relation='res.company',
            string='Company',
            store=True,
            readonly=True
        ),
        'invoice_id': fields.many2one(
            'account.invoice',
            string='Invoice',
            domain=['|', ('active', '=', False), ('active', '=', True)],
            help='Related original Customer invoice'
        ),
        'pay_by_email_url': fields.char('Pay by e-mail URL', size=256),
        'unclaimed_price': fields.integer('Price for unclaimed return'),
    }

    def _send_unclaimed_reminders(self, cr, uid, context=None):
        """
            Cron method to send reminders on unresponded claims
        """
        model_data_obj = self.pool['ir.model.data']
        template_obj = self.pool['email.template']
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        initial_categ_id = user.company_id.unclaimed_initial_categ_id.id
        first_reminder_categ_id = \
            user.company_id.unclaimed_first_reminder_categ_id.id
        second_reminder_categ_id = \
            user.company_id.unclaimed_first_reminder_categ_id.id
        query = """
            SELECT id
            FROM crm_claim
            WHERE categ_id = %s
            AND create_date <
                (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - INTERVAL '%s DAYS')
            AND id NOT IN (
                SELECT claim_id
                FROM stock_picking
                WHERE claim_id IS NOT NULL
                AND type = 'out'
            )
        """

        # Get all claims for first reminder
        cr.execute(query, (initial_categ_id, 30))
        first_remainder_claim_ids = [x[0] for x in cr.fetchall()]
        for claim_id in first_remainder_claim_ids:
            """ send e-mail """
            _, template_id = model_data_obj.get_object_reference(
                cr, uid, 'crm_claim_mail',
                'email_template_rma_first_reminder')
            template_obj.send_mail(cr, uid, template_id,
                                   claim_id, context=context)
            self.write(cr, uid, [claim_id],
                       {'categ_id': first_reminder_categ_id},
                       context=context)
            self.case_close(cr, uid, [claim_id], context=context)

        # Get all claims for second reminder
        cr.execute(query, (first_reminder_categ_id, 60))
        second_remainder_ids = [x[0] for x in cr.fetchall()]
        for claim_id in second_remainder_ids:
            """ send e-mail """
            _, template_id = model_data_obj.get_object_reference(
                cr, uid, 'crm_claim_mail',
                'email_template_rma_second_reminder')
            template_obj.send_mail(cr, uid, template_id,
                                   claim_id, context=context)
            self.write(cr, uid, [claim_id],
                       {'categ_id': second_reminder_categ_id},
                       context=context)
            self.case_close(cr, uid, [claim_id], context=context)

        return True


