# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
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
"""Module for the StatementLoadPolicy."""
import simplejson as json
from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

from ..backend import file_import_s3
from openerp.addons.connector_file.unit.policy import LoadPolicy


@file_import_s3
class StatementLoadPolicy(LoadPolicy):

    """Policy to load a chunk into an account.bank.statement.

    This uses the openerp standard load().

    """

    _model_name = 'file.chunk.binding'

    def load_one_chunk(self, chunk_b_id):
        """Load a chunk into an OpenERP Journal Entry."""

        s = self.session
        statement_obj = s.pool['account.bank.statement']
        chunk_b_obj = s.pool[self._model_name]
        chunk_b = chunk_b_obj.browse(s.cr, s.uid, chunk_b_id,
                                     context=s.context)

        if chunk_b.load_state != 'pending':
            return

        prepared_header = json.loads(chunk_b.prepared_header)
        prepared_data = json.loads(chunk_b.prepared_data)
        load_result = statement_obj.load(
            s.cr,
            s.uid,
            prepared_header,
            prepared_data,
            context=s.context,
        )

        assert not load_result['ids'] or len(load_result['ids']) <= 1, """
            One chunk should always generate one move, or an error.
            More than one should not happen.
        """

        if load_result['ids']:
            chunk_b.write({
                'statement_id': load_result['ids'][0],
                'sync_date': datetime.now().strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT
                ),
                'load_state': 'done',
            })
        else:
            chunk_b.write({
                'load_state': 'failed',
                'exc_info': (
                    u'Error during load() of the bank statement.\n{0}'.format(
                        load_result['messages']
                    )
                )
            })
