# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, fields
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    qoqa_id = fields.Char(string='ID on QoQa', index=True, copy=False)


@qoqa
class CurrencyBinder(QoQaDirectBinder):
    _model_name = 'res.currency'

    def to_openerp(self, external_id, unwrap=False):
        # find by id
        _super = super(CurrencyBinder, self)
        bindings = _super.to_openerp(external_id, unwrap=unwrap)
        if not bindings:
            # find by name ('chf')
            bindings = self.model.with_context(active_test=False).search(
                [('name', '=ilike', str(external_id))]
            )
            if not bindings:
                return self.model.browse()
            bindings.ensure_one()
        return bindings
