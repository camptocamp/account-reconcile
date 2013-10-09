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

{'name': 'QoQa Connector',
 'version': '0.0.1',
 'category': 'Connector',
 'depends': ['connector',
             'sale',
             'qoqa_offer',
             ],
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'website': 'http://www.camptocamp.com',
 'description': """
QoQa Connector
==============

Synchronize OpenERP with the different QoQa Stores
(qoqa.ch, qwine.ch, qsport.ch, qooking.ch).

""",
 'images': [],
 'demo': [],
 'data': ['data.xml',
          'wizard/qoqa_backend_oauth_view.xml',
          'qoqa_model_view.xml',
          'qoqa_menu.xml',
          'res_company_view.xml',
          'product_view.xml',
          'account_tax_view.xml',
          'qoqa_buyphrase_view.xml',
          'security/ir.model.access.csv',
          ],
 'installable': True,
 'application': True,
}
