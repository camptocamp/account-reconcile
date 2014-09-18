# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

from openerp.osv import orm
from openerp.tools.translate import _


class picking_dispatch_delayed_done(orm.TransientModel):
    _name = 'picking.dispatch.delayed.done'
    _description = 'Picking Dispatch Delayed Done'

    def delayed_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        dispatch_ids = context.get('active_ids')
        if not dispatch_ids:
            raise orm.except_orm(
                _('Error'),
                _('No selected picking dispatch'))

        dispatch_obj = self.pool['picking.dispatch']
        domain = [('state', '=', 'progress'),
                  ('id', 'in', dispatch_ids)]
        check_ids = dispatch_obj.search(cr, uid, domain, context=context)
        if dispatch_ids != check_ids:
            raise orm.except_orm(
                _('Error'),
                _('All the picking dispatches must be in progress to '
                  'be set to done.'))
        dispatch_obj.action_delayed_done(cr, uid, dispatch_ids,
                                         context=context)
        return {'type': 'ir.actions.act_window_close'}
