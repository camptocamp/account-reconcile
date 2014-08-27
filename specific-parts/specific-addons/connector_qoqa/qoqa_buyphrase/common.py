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
from ..unit.backend_adapter import QoQaAdapter
from ..backend import qoqa


class qoqa_buyphrase(orm.Model):
    _inherit = 'qoqa.buyphrase'

    _columns = {
        'backend_id': fields.related(
            'qoqa_shop_id', 'backend_id',
            type='many2one',
            relation='qoqa.backend',
            string='QoQa Backend',
            readonly=True),
        'qoqa_id': fields.char('ID on QoQa', select=True),
        'qoqa_sync_date': fields.datetime('Last synchronization date'),
    }

    def copy_data(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'qoqa_id': False,
        })
        return super(qoqa_buyphrase, self).copy_data(
            cr, uid, id, default=default, context=context)


@qoqa
class BuyphraseAdapter(QoQaAdapter):
    _model_name = 'qoqa.buyphrase'
    _endpoint = 'buyphrase'
