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
Models that represent the structure of the QoQa Stores.
We'll have 1 ``qoqa.backend`` (sharing the connection informations probably),
linked to several ``qoqa.store``.

Both models will act as 'connector.backend', that means that each time we
build an :py:class:`~openerp.addons.connector.connector.Environment`, we'll
pass it either a ``qoqa.backend``, either a ``qoqa.store``. Each store will
have a different :py:class:`~openerp.addons.backend.Backend` version.

"""

class qoqa_backend(orm.Model):
    _name = 'qoqa.backend'
    _description = 'QoQa Backend'
    _inherit = 'connector.backend'
    _backend_type = 'qoqa'

    _columns = {
        # override because the version has no meaning here
        'version': fields.dummy('Version'),
    }

    def check_connection(self, cr, uid, ids, context=None):
        raise NotImplementedError

    def get_backend(self, cr, uid, id, context=None):
        """ For a record of backend, returns the appropriate instance
        of :py:class:`~connector.backend.Backend`.

        Override: force to use the main backend because the versions
        are really used in the ``qoqa.store`` records.
        """
        return qoqa

    def create(self, cr, uid, vals, context=None):
        existing_ids = self.search(cr, uid, [], context=context)
        if existing_ids:
            raise orm.except_orm(
                _('Error'),
                _('Only 1 QoQa configuration is allowed.'))
        return super(qoqa_backend, self).create(cr, uid, vals, context=context)


class qoqa_store(orm.Model):
    _name = 'qoqa.store'
    _description = 'QoQa Store'
    # should be _inherit'ed from connector.backend, but it adds a 'name'
    # fields which comes on top of sale.shop's name and prevent
    # creation of a qoqa.store
    # _inherit = 'connector.backend'
    _inherits = {'sale.shop': 'openerp_id'}
    _backend_type = 'qoqa'

    def _select_versions(self, cr, uid, context=None):
        """ Available versions

        Can be inherited to add custom versions.
        """
        return [('qoqa.ch', 'QoQa.ch'),
                ('qoqa.fr', 'QoQa.fr'),
                ('qwine.ch', 'Qwine.ch'),
                ('qwine.fr', 'Qwine.fr'),
                ('qsport.ch', 'Qsport.ch'),
                ('qstyle.ch', 'Qstyle.ch'),
                ('qooking.ch', 'Qooking.ch'),
                ('generic', 'Generic'),
                ]

    _columns = {
        'version': fields.selection(
            lambda self, *args, **kwargs: self._select_versions(*args, **kwargs),
            string='Version',
            required=True),
        'backend_id': fields.many2one(
            'qoqa.backend',
            string='Backend',
            required=True,
            ondelete='restrict'),
        'openerp_id': fields.many2one(
            'sale.shop',
            string='Sale Shop',
            required=True,
            readonly=True,
            ondelete='cascade'),
    }

    _defaults = {
        'version': 'generic',
    }

    def get_backend(self, cr, uid, id, context=None):
        """ For a record of backend, returns the appropriate instance
        of :py:class:`~connector.backend.Backend`.

        Override: when the selected version is 'generic',
        returns the :py:class:`~connector.backend.Backend` of the related
        ``qoqa.backend``.
        """
        if hasattr(id, '__iter__'):
            assert len(id) == 1, "One ID expected, got: %r" % id
            id = id[0]
        store = self.browse(cr, uid, id, context=context)

        if store.version == 'generic':
            return store.backend_id.get_backend()

        backend_record = self.browse(cr, uid, id, context=context)
        return backend.get_backend(self._backend_type, backend_record.version)
