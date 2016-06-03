# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA (Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'QoQa Claim Unclaimed Process',
    'version': '9.0.1.0.0',
    'category': 'Others',
    'depends': [
        'crm_claim_mail',
        'connector_qoqa',
        'email_template_dateutil'
    ],
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'description': """
        QoQa Claim Unclaimed Process
        ============================

        Specific processed for unclaimed packages returns,
        reminders and new deliveries.

        """,
    'images': [],
    'demo': [],
    'data': [
        'data/claim_data.xml',
        'data/email_template.xml',
        'views/company_view.xml',
        'wizard/crm_claim_unclaimed_view.xml',
    ],
    'installable': False,
    'application': True,
}
