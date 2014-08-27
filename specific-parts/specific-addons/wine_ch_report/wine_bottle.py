# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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


def volume_to_string(value, unit='l'):
    prefix = ''
    if value < 1:
        value *= 100
        prefix = 'c'
    value = ('%.2f' % value).rstrip('0').rstrip('.')
    return value + ' ' + prefix + unit


class wine_bottle(orm.Model):
    """ The bottle is used to define the capacity of wine bottles.

    It is needed in report to compute sums as we receive a qantity
    of bottle this needs to be translated in litres.
    """
    _name = 'wine.bottle'
    _description = 'Wine Bottle'

    _order = 'volume'

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]
        bottles = self.read(cr, uid, ids, ['name', 'volume'],
                            context=context)
        res = []
        for record in bottles:
            record['volume'] = volume_to_string(record['volume'])
            name = '%(name)s (%(volume)s)' % record
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Name', required=True),
        'complete_name': fields.function(
            _name_get_fnc,
            type='char',
            string='Complete name'),
        'code': fields.char('Code'),
        'volume': fields.float('Volume', required=True),
        }
