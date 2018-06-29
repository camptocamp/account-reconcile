# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{'name': 'QoQa Base Data',
 'version': '0.0.1',
 'category': 'Others',
 'depends': [
     'sale',
     'connector_ecommerce',
 ],
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'website': 'http://www.camptocamp.com',
 'description': """
QoQa Base Data
==============

Create data used by other modules (connector_qoqa, wine_ch_report, ...),
as the attribute sets, ...

""",
 'images': [],
 'demo': [],
 'data': [
     'lang_install.xml',
     'picking_type.xml',
     'product.xml',
     'product_category.xml',
     'res_company_view.xml',
 ],
 'installable': True,
 'application': True,
 }
