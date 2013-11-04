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

import logging

from openerp.addons.connector.unit.mapper import (mapping,
                                                  only_create,
                                                  ImportMapper,
                                                  )
from ..backend import qoqa
from ..unit.import_synchronizer import (FromDateDelayBatchImport,
                                        QoQaImportSynchronizer,
                                        )

_logger = logging.getLogger(__name__)


@qoqa
class ResPartnerBatchImport(FromDateDelayBatchImport):
    """ Import the QoQa Users.

    For every product in the list, a delayed job is created.
    Import from a date
    """
    _model_name = 'qoqa.res.partner'


@qoqa
class ResPartnerImport(QoQaImportSynchronizer):
    _model_name = 'qoqa.res.partner'


@qoqa
class ResPartnerImportMapper(ImportMapper):
    _model_name = 'qoqa.res.partner'

    direct = [('created_at', 'created_at'),
              ('updated_at', 'updated_at'),
              ('suspicious', 'suspicious'),
              ('is_active', 'qoqa_active'),
              ('email', 'email'),
              ]

    @only_create
    @mapping
    def name(self, record):
        name = ' '.join((record['firstname'], record['lastname']))
        return {'name': name}
