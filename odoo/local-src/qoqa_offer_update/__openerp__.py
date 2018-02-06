# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Qoqa VAT Update',
    'summary': 'Update VAT of SO/INV related to Offer',
    'version': '9.0.1.0.0',
    'category': 'accont-financial-tools',
    'depends': [
        'qoqa_offer',
    ],
    'author': "Camptocamp SA",
    'license': 'AGPL-3',
    'website': 'http://www.camptocamp.com',
    'data': [
        'wizard/qoqa_offer_update_view.xml',
    ],

    'installable': True,
    'application': False,
}
