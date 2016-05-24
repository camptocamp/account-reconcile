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

from openerp.tools.config import config
from openerp.addons.web.controllers import main

from openerp.addons.web import http


class HomeEnv(main.Home):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        response = super(HomeEnv, self).web_client(s_action=s_action, **kw)
        response.qcontext['env'] = config['running_env']
        return response
