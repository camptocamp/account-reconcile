# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
 'depends': ['stock'],
 'data': [],
 'test': [],
 'installable': True,
 'auto_install': False,
 'application': True,
 }
