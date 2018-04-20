# -*- coding: utf-8 -*-
# © 2016-2017 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'QoQa Claim Unclaimed Process',
    'version': '9.0.1.0.1',
    'category': 'Others',
    'depends': [
        'crm_claim_mail',
        'crm_rma_by_shop',
        # TODO import connector_qoqa when pay_by_email API is available
        # 'connector_qoqa'
    ],
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'images': [],
    'demo': [],
    'data': [
        'data/claim_data.xml',
        'data/mail_template.xml',
        'views/company_view.xml',
        'views/package.xml',
        'wizard/claim_make_picking.xml',
        'wizard/crm_claim_unclaimed_view.xml',
    ],
    'installable': True,
    'application': True,
}
