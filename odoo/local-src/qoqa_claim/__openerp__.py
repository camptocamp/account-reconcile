# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA (Joël Grandguillaume, Matthieu Dietrich)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'QoQa Claim Specifics',
    'version': '9.0.1.0.0',
    'category': 'Others',
    'depends': [
        'mail',
        'crm_claim_rma',
        'crm_claim_type',
    ],
    'author': 'Camptocamp',
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'description': """
        QoQa Claim Specific
    """,
    'images': [],
    'demo': [],
    'data': [
        'security/claim_groups.xml',
        'data/crm_claim_data.xml',
        'data/mail_template.xml',
        'views/crm_claim_stage.xml',
        'views/crm_claim_view.xml',
        'views/crm_claim_line.xml',
        'views/stock_picking.xml',
        'views/crm_claim_category.xml',
        'views/crm_team.xml',
        'views/mail_alias.xml',
        'views/claim_menus.xml',
    ],
    'installable': True,
    'application': True,
}
