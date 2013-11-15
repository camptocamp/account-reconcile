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

{'name': 'QoQa Base Data',
 'version': '0.0.1',
 'category': 'Others',
 'depends': ['product_custom_attributes',
             'sale',
             'connector_ecommerce',
             ],
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'website': 'http://www.camptocamp.com',
 'description': """
QoQa Base Data
==============

Create data used by other modules (connector_qoqa, wine_ch_report, ...),
as the attribute sets, ...

""",
 'images': [],
 'demo': [],
 'data': ['attribute_set.xml',
          'sale_shop.xml',
          'product.xml',
          ],
 'installable': True,
 'application': True,
}
