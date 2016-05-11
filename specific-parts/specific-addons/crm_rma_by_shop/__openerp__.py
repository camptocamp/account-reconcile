# -*- coding: utf-8 -*-
# Author: Joel Grand-Guillaume
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'RMA Claims by shop',
    'version': '9.0.1.0.0',
    'category': 'Generic Modules/CRM & SRM',
    'depends': [
        'crm_claim',
        'qoqa_offer'
    ],
    'author': "Camptocamp, Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'description': """
RMA Claim by shops
==================

Claim improvements to use them by shops:

 * Add shop on claim
 * Add various filter in order to work on a basic "by shop" basis
""",
    'images': [],
    'demo': [],
    'data': [
        'views/crm_claim.xml',
    ],
    'installable': True,
    'application': True,
}
