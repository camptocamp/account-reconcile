# -*- coding: utf-8 -*-

##############################################################################
#
# Author: Tristan Rouiller
# Copyright 2014 QoQa Services SA
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

from openerp.tools.config import config
from openerp.addons.web.controllers import main

from openerp.addons.web import http

import re


class HomeEnv(main.Home):
    _cp_path = '/'

    @http.httprequest
    def index(self, req, s_action=None, db=None, **kw):
        html_template = super(HomeEnv, self).index(req, s_action=s_action,
                                                   db=db, **kw)
        environment_name = config['running_env']

        body_replace = "<body env='%(environment_name)s'" % {
            'environment_name': environment_name,
        }

        return re.sub(r"<body", body_replace, html_template)
