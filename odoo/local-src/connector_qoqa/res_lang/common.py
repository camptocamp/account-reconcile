# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models
from ..unit.binder import QoQaDirectBinder
from ..backend import qoqa


@qoqa
class ResLangBinder(QoQaDirectBinder):
    _model_name = 'res.lang'

    def to_openerp(self, external_id, unwrap=False):
        binding = self.model.search(
            [('code', '=like', '{}_%'.format(external_id))],
            limit=1,
        )
        if not binding:
            return self.model.browse()
        binding.ensure_one()
        return binding

    def to_backend(self, binding_id, wrap=False):
        record = self.model.browse()
        if isinstance(binding_id, models.BaseModel):
            binding_id.ensure_one()
            record = binding_id
            binding_id = binding_id.id
        if not record:
            record = self.model.browse(binding_id)
        assert record
        return record.code[:2]
