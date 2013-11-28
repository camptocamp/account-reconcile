# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


class payment_method(orm.Model):
    _inherit = 'payment.method'

    _columns = {
        'qoqa_id': fields.char('ID on QoQa'),
        'sequence': fields.integer(
            'Priority',
            help="When a sales order has been paid with "
                 "several payment methods, the sales order "
                 "will be assigned to the first method found, "
                 "according to their priority.\n"
                 "This impacts the automatic workflow applied to "
                 "the sales order."
        ),
        # TODO: not used actually, consider removal
        # because configured with a journal, a payment
        # can be generated for the gift card, mimiting
        # what is happening on the QoQa backend
        'gift_card': fields.boolean(
            'Gift Card',
            help="Generates a gift line in the sales order."
        ),
        'active': fields.boolean('Active'),
    }

    _defaults = {
        'active': True,
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_id': False,
        })
        return super(payment_method, self).copy_data(
            cr, uid, id, default=default, context=context)


@qoqa
class PaymentMethodBinder(QoQaDirectBinder):
    _model_name = 'payment.method'

    def to_openerp(self, external_id, unwrap=False, company_id=None):
        assert company_id
        with self.session.change_context(dict(active_test=False)):
            binding_ids = self.session.search(
                self.model._name,
                [('qoqa_id', '=', str(external_id)),
                 '|', ('company_id', '=', company_id),
                      ('company_id', '=', False)])
        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        return binding_ids[0]
