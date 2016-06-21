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

{
    'name': 'S3 move import',
    'version': '9.0.1.0.0',
    'category': 'Finance',
    'author': 'Camptocamp SA',
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    'depends': [
        'account_move_base_import',
        'server_environment',
        'server_environment_files',
    ],
    'data': [
        "views/journal_view.xml",
    ],
    'external_dependencies': {
        'python': ['boto'],
    },
    'installable': True,
}
