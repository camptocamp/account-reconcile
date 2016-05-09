# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{'name': 'Swiss Post - PP Frankling',
 'version': '9.0.1.0.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'category': 'Delivery',
 'complexity': 'normal',
 'depends': [
     'report',
     'base_delivery_carrier_label',
     'configuration_helper',
     'crm_claim_rma',
     'qoqa_offer',
     ],
 'description': """
This print a basic label using webkit library inserting a pp franking image
as an exemple you can print labels with a "A priority" PP franking for
A priority mailing

It also allows to use shop logo

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>

 """,
 'website': 'http://www.camptocamp.com/',
 'data': [
     'data/paperformat.xml',
     'views/sale.xml',
     'views/res_config.xml',
     'views/report_shipping_label.xml',
     ],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': True}
