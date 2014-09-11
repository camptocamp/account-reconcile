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


class picking_dispatch(orm.Model):
    _inherit = 'picking.dispatch'

    def __init__(self, pool, cr):
        super(picking_dispatch, self).__init__(pool, cr)
        state = self._columns['state']
        selection = state.selection
        if not any('delayed_done' == choice[0] for choice in selection):
            selection.append(('delayed_done', 'Delayed Done'))

    def action_delayed_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'delayed_done'}, context=context)
        return True

    def _scheduler_delayed_done(self, cr, uid, context=None):
        """ Called from the Scheduled Actions.

        Warning: it commits after each dispatch so it should not be
        called outside of the scheduled actions
        """
        partial_move_obj = self.pool["stock.partial.move"]
        dispatch_ids = self.search(cr, uid, [('state', '=', 'delayed_done')],
                                   context=context)
        for dispatch_id in dispatch_ids:
            action = self.action_done(cr, uid, [dispatch_id], context=context)
            partial_id = action['res_id']
            partial_move_obj.do_partial(cr, uid, [partial_id], context=context)
            cr.commit()
