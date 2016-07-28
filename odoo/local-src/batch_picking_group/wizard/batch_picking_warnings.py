# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models


class PickingWarnings(models.TransientModel):
    _name = 'stock.batch.group.warnings'

    @api.multi
    def _default_message(self):
        warning_ids = self.env.context.get('warning_picking_ids')

        pickings = self.env['stock.picking'].browse(warning_ids)
        message = _(
            "The following pickings were ignored because they contain "
            "zero or more than one package:"
        )
        message += "<ul>"
        for picking in pickings:
            message += "<li>%s</li>" % picking.name
        message += "</ul>"

        return '%s' % message

    batch_domain = fields.Char(
        required=True, readonly=True,
        default=lambda self: self.env.context.get('batch_domain')
    )
    message = fields.Html(required=True, default=_default_message)

    @api.multi
    def action_ok(self):
        self.ensure_one()
        return {
            'domain': self.batch_domain,
            'name': _('Generated Batches'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.batch.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
