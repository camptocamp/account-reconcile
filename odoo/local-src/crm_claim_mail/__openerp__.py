# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'QoQa CRM Claim Mail',
    'version': '1.1',
    'author': 'Camptocamp',
    'maintainer': 'Camptocamp',
    'license': 'AGPL-3',
    'category': 'Customer Relationship Management',
    'depends': [
        'crm_claim_merge',
        'qoqa_base_data',
        'qoqa_claim'
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
    'data': [
        'data/lang_install.xml',
        'data/reopen_claim_on_mail.xml',
        'data/send_mail_on_new_claim.xml',
        'views/res_company_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
