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
        'crm_rma_by_shop',
        'crm_claim_merge',
        'qoqa_base_data',
        'qoqa_claim',
        'qoqa_offer'
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'data/reopen_claim_on_mail.xml',
        'data/send_mail_on_new_claim.xml',
        'data/claim_filter.xml',
        'views/qoqa_shop_view.xml',
        'views/res_company_view.xml',
        'views/mail_template.xml',
        'views/crm_claim.xml',
    ],
    'installable': True,
    'auto_install': False,
}
