# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{'name': 'QoQa Products',
 'summary': 'Products customizations',
 'version': '9.0.1.0.1',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Sales',
 'depends': ['product',
             'product_brand',  # oca/product-attribute
             'product_variant_exclusion',  # oca/product-attribute
             ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'security/ir.model.access.csv',
     'data/wine_data.xml',
     'views/product_views.xml',
     'views/wine_views.xml',
 ],
 'installable': True,
 }
