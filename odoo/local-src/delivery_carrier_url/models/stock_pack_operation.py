# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Tristan Rouiller
#    Copyright 2014 QoQa Services SA
#    Copyright 2016 Camptocamp SA
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

from openerp import _, api, exceptions, fields, models


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    def _get_tracking_url(self):
        user = self.env.user

        if user.lang:
            lang = user.lang.split('_')[0]
        else:
            lang = 'fr'

        for op in self:
            if not op.picking_id or not op.picking_id.carrier_id.url_template:
                continue
            tracking_number = op.result_package_id.parcel_tracking
            if not tracking_number:
                tracking_number = op.picking_id.carrier_tracking_ref
            if not tracking_number:
                continue
            op.tracking_url = op.picking_id.carrier_id.url_template % {
                'tracking_number': tracking_number,
                'lang': lang,
            }

    tracking_url = fields.Char(compute=_get_tracking_url,
                               string='Tracking url')

    @api.multi
    def open_tracking_url(self):
        self.ensure_one()

        if not self.tracking_url:
            raise exceptions.UserError(
                _('No tracking url exist'))

        return {'type': 'ir.actions.act_url',
                'target': 'new',
                'url': self.tracking_url}
