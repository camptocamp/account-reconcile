# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, api

from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.unit.mapper import ExportMapper
from openerp.addons.connector.exception import NoConnectorUnitError

from ..connector import get_environment


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.multi
    def write(self, vals):
        res = super(IrTranslation, self).write(vals)
        for record in self:
            if record._has_to_export_to_qoqa():
                record._export_to_qoqa()
        return res

    @api.multi
    def _has_to_export_to_qoqa(self):
        # The whole method is too restrictive to work on all cases:
        # - the record must have a field 'qoqa_bind_ids' that points to the
        #   bindings
        # - the export mapper must have a 'translatable_fields' attribute
        #   that contains a list of translatable fields to export
        # Also, consecutive translations on several languages will trigger
        # a new export job each time.
        self.ensure_one()
        if (self.type != 'model' or
                not self.res_id or
                not self.state == 'translated'):
            return False
        model_name, field = self.name.split(',')
        model = self.env[model_name]
        if 'qoqa_bind_ids' not in model._fields:
            return
        record = model.browse(self.res_id)
        bindings = record.qoqa_bind_ids
        session = ConnectorSession.from_env(self.env)
        backend = self.env['qoqa.backend'].get_singleton()
        with get_environment(session, bindings._model._name,
                             backend.id) as conn_env:
            try:
                mapper = conn_env.get_connector_unit(ExportMapper)
            except NoConnectorUnitError:
                return False
            translatable_fields = [f[0] for f in
                                   getattr(mapper, 'translatable_fields', [])]
            if field in translatable_fields:
                return True
        return False

    @api.multi
    def _export_to_qoqa(self):
        model_name, __ = self.name.split(',')
        model = self.env[model_name]
        record = model.browse(self.res_id)
        # touch in order to trigger the export
        for binding in record.qoqa_bind_ids:
            binding.backend_id = binding.backend_id
