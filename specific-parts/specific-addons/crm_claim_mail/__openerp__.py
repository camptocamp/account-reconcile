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
 'version': '1.1',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Customer Relationship Management',
 'depends': ['crm_claim_rma',  # in lp:openerp-rma
             'crm_claim_merge',  # in lp:openerp-crm
             'qoqa_base_data',
             ],
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
* When a new claim is created, an email is sent to the customer and the claim
 is set to the stage 'In Progress'.
* When an email is received on an existing claim, the claim is set back to a
  new stage "Response Received"

** WARNING **
This module installs the fr_FR and de_DE languages.

 """,
 'website': 'http://www.camptocamp.com',
 'data': ['lang_install.xml',
          'send_mail_on_new_claim.xml',
          'reopen_claim_on_mail.xml',
          'res_company_view.xml',
          'crm_claim_view.xml',
          'sale_shop_view.xml',
          ],
 'installable': True,
 'auto_install': False,
 }
