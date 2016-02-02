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
"""Units for processing chunks."""

from openerp.addons.connector_file.unit.chunk import ChunkLoader
from ..backend import file_import_s3

from ..unit.statement_load_policy import StatementLoadPolicy


class S3ChunkLoader(ChunkLoader):

    @property
    def load_policy_instance(self):
        """ Return an instance of ``StatementLoadPolicy``.

        The instantiation is delayed because some synchronizations do
        not need such a unit and the unit may not exist.

        """
        if self._load_policy_instance is None:
            self._load_policy_instance = (
                self.environment.get_connector_unit(StatementLoadPolicy)
            )
        return self._load_policy_instance


@file_import_s3
class AsyncChunkLoader(S3ChunkLoader):

    """Async-specific code."""

    pass
