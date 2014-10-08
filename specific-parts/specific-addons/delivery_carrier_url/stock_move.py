# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Tristan Rouiller
#    Copyright 2014 QoQa Services SA
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
from openerp.tools.translate import _


class stock_move(orm.Model):
    _inherit = 'stock.move'

    def _get_tracking_url(self, cr, uid, ids, name, args, context=None):
        stock_moves = self.browse(cr, uid, ids, context=context)
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)

        if user.lang:
            lang = user.lang.split('_')[0]
        else:
            lang = 'fr'

        tracking_urls = {}
        for sm in stock_moves:
            if not sm.picking_id or not sm.picking_id.carrier_id.url_template:
                tracking_urls[sm.id] = False
                continue
            tracking_number = False
            if sm.tracking_id:
                tracking_number = sm.tracking_id.serial
            if not tracking_number:
                tracking_number = sm.picking_id.carrier_tracking_ref
            if not tracking_number:
                tracking_urls[sm.id] = False
                continue
            tracking_urls[sm.id] = sm.picking_id.carrier_id.url_template % {
                'tracking_number': tracking_number,
                'lang': lang,
            }
        return tracking_urls

    _columns = {
        'tracking_url': fields.function(_get_tracking_url, type='char',
                                        string='Tracking url'),
    }

    def open_tracking_url(self, cr, uid, ids, context=None):

        assert len(ids) == 1, "One id expected"
        stock_moves = self.browse(cr, uid, ids, context=context)
        sm = stock_moves[0]

        if not sm.tracking_url:
            raise orm.except_orm(
                _('Error'),
                _('No tracking url exist'))

        return {'type': 'ir.actions.act_url',
                'target': 'new',
                'url': sm.tracking_url}
