# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    qoqa_id = fields.Char(string='ID on QoQa', index=True, copy=False)
    sequence = fields.Integer(
        string='Priority',
        help="When a sales order has been paid with "
             "several payment methods, the sales order "
             "will be assigned to the first method found, "
             "according to their priority.\n"
             "This impacts the automatic workflow applied to "
             "the sales order.",
    )
    gift_card = fields.Boolean(
        string='Gift Card',
        help="Generates a gift line in the sales order."
    )
    payment_cancellable_on_qoqa = fields.Boolean(
        string='The payments can be cancelled (same day)',
        default=True,
    )
    payment_settlable_on_qoqa = fields.Boolean(
        string='The payments must be settled',
        default=False,
    )


@qoqa
class PaymentModeBinder(QoQaDirectBinder):
    _model_name = 'account.payment.mode'

    def to_openerp(self, external_id, unwrap=False, company_id=None):
        assert company_id
        bindings = self.model.with_context(active_test=False).search(
            [(self._external_field, '=', str(external_id)),
             '|', ('company_id', '=', company_id),
                  ('company_id', '=', False)],
        )
        if not bindings:
            return self.model.browse()
        bindings.ensure_one()
        return bindings
