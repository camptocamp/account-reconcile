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

{'name': 'Picking Dispatch Delay Done',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Warehouse Management',
 'depends': ['picking_dispatch',  # stock-logistics-workflow
             ],
 'description': """
Picking Dispatch Delay Done
===========================

Adds a button on the Picking Dispatches allowing to set the dispatch to done,
later. A cron will process them so the user is not blocked.
Add a state on the picking dispatches 'Delayed Done'.

""",
 'website': 'http://www.camptocamp.com',
 'data': ['picking_dispatch_view.xml',
          'cron_data.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
