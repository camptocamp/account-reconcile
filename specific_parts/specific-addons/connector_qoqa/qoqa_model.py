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
from openerp.tools.translate import _
from openerp.addons.connector import backend
from .backend import qoqa

"""
Models that represent the structure of the QoQa Shops.
We'll have 1 ``qoqa.backend`` (sharing the connection informations probably),
linked to several ``qoqa.shop``.

Both models will act as 'connector.backend', that means that each time we
build an :py:class:`~openerp.addons.connector.connector.Environment`, we'll
pass it either a ``qoqa.backend``, either a ``qoqa.shop``. Each shop will
have a different :py:class:`~openerp.addons.backend.Backend` version.

"""

class qoqa_backend(orm.Model):
    _name = 'qoqa.backend'
    _description = 'QoQa Backend'
    _inherit = 'connector.backend'
    _backend_type = 'qoqa'

    def _select_versions(self, cr, uid, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('1.0', '1.0'),
                ]

    _columns = {
        # override because the version has no meaning here
        'version': fields.selection(
            _select_versions,
            string='Version',
            required=True),
    }

    def check_connection(self, cr, uid, ids, context=None):
        raise NotImplementedError

    def create(self, cr, uid, vals, context=None):
        existing_ids = self.search(cr, uid, [], context=context)
        if existing_ids:
            raise orm.except_orm(
                _('Error'),
                _('Only 1 QoQa configuration is allowed.'))
        return super(qoqa_backend, self).create(cr, uid, vals, context=context)


class qoqa_shop(orm.Model):
    _name = 'qoqa.shop'
    _description = 'QoQa Shop'
    _inherits = {'sale.shop': 'openerp_id'}

    _columns = {
        'backend_id': fields.many2one(
            'qoqa.backend',
            string='Backend',
            required=True,
            readonly=True,
            ondelete='restrict'),
        'openerp_id': fields.many2one(
            'sale.shop',
            string='Sale Shop',
            required=True,
            readonly=True,
            ondelete='cascade'),
    }
