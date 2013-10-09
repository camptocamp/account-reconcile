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


class wine_class(orm.Model):
    """ The class is used on the reports to group the wines.

    The tree is something as follows (excerpt)::

        10 Classe AOC
          110 Suisse occidentale
            Vaud
            Valais
          120 Suisse orientale
            Zurich
            Autres cantons
          130 Tessin
        20 Classe Vin de pays
          Suisse occidentale
          Suisse orientale
          Vin Suisse

    Only the leaves can be assigned on products.
    It is close to the regions, but not necessarily, sometimes, a leaf
    is a region, sometimes a country, or a 'other'.
    """
    _name = 'wine.class'
    _description = 'Wine Class'

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (long, int)):
            ids = [ids]
        classes = self.read(cr, uid, ids, ['name', 'parent_id'],
                            context=context)
        res = []
        for record in classes:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
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
        'parent_id': fields.many2one('wine.class', string='Parent class'),
        'child_ids': fields.one2many('wine.class', 'parent_id',
                                     string='Children classes'),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
    }

    def check_recursion(self, cr, uid, ids, context=None, parent=None):
        check = super(wine_class, self)._check_recursion(
            cr, uid, ids, context=context, parent=parent)
        return check

    _constraints = [
        (check_recursion,
         'Error! You cannot create recursive wine classes.',
         ['parent_id'])
    ]
