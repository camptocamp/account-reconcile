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


{'name': 'QoQa CRM Claim Mail',
 'version': '1.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Customer Relationship Management',
 'depends': ['crm_claim_rma'],
 'description': """
CRM Claim Mail
==============

Customizations for QoQa on CRM and e-mails.
This is specific because it makes assumptions about how the setup is done.
Exemple: the number of the claims should be RMA-\\d+

Features:

* When an email cannot be linked with its originating claim with the
 'In-Reply-To' or 'References' header, it tries to match it with it
 number. The numbers of the claims must start with RMA-

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['mail_data.xml',
          ],
 'installable': True,
 'auto_install': False,
}
