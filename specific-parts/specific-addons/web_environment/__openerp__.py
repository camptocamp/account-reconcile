# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Tristan Rouiller
# Copyright 2014 QoQa Services SA
# Author: Yannick Vaucher
# Copyright 2016 Camptocamp SA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{'name': 'Web environnment',
 'version': '9.0.1.0',
 'category': 'Others',
 'depends': ['web',
             'server_environment',
             ],
 'author': 'QoQa',
 'license': 'AGPL-3',
 'website': 'http://www.qoqa.com',
 'description': """
Use the environment to change the layout style
==============================================

We add a variable `env` in qweb context that we use
to define later the style to use.
""",
 'images': [],
 'demo': [],
 'data': ['views/web_environment_template.xml'],
 'installable': True,
 'application': True,
 'bootstrap': True,
 }
