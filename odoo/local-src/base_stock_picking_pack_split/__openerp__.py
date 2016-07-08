# -*- coding: utf-8 -*-
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{'name': 'Base stock picking pack split',
 'version': '1.0',
 'category': 'Warehouse',
 'description': """
Split picking per pack
======================

This module adds a function on stock.picking to divide it in mutiple packs
based on a simple rule. In the future it could be the base of more complex
packaging.

The basic function of this module is a simple maximum of product a pack
can contain. In case of multiple packs we consider that all products
have the same size.

So different products can be added in a same pack.

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>

""",
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['stock', 'delivery'],  # delivery not needed, only to pass tests
 'data': ['wizard/split_packs_view.xml',
          ],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 }
