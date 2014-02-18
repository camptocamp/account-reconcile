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
{'name': 'QoQa Label dispatch and pack slit',
 'version': '1.0',
 'category': 'QoQa',
 'description': """
QoQa specific - Number of product on dispatch Label generation
==============================================================

This module adds a number of product per pack on the picking wizard
to generate related picking labels

TO REMOVE: the wizard has been extracted into an individual wizard
in picking_dispatch_grouper

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>

""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['delivery_carrier_label_dispatch',
             'base_stock_picking_pack_split',
             ],
 'data': [
     ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 }
