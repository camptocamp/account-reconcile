# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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
{'name': 'Swiss Post - PP Frankling',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'version',
 'complexity': 'normal',
 'depends': [
     'base_delivery_carrier_label',
     'report_webkit',
     'configuration_helper',
     ],
 'description': """
This print a basic label using webkit library inserting a pp franking image
as an exemple you can print labels with a "A priority" PP franking for
A priority mailing

It also allows to use shop logo

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>

 """,
 'website': 'http://www.camptocamp.com/',
 'data': [
     'base_headers_data.xml',
     'reports.xml',
     'sale_view.xml',
     'res_config_view.xml',
     ],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True}
