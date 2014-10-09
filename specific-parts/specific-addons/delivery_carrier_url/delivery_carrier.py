# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Tristan Rouiller
#    Copyright 2014 QoQa Services SA
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

from openerp.osv import orm, fields


class delivery_carrier(orm.Model):
    _inherit = 'delivery.carrier'

    _columns = {
        'url_template': fields.char(
            string='Url template',
            help="The '%(tracking_number)s' sequence will be replaced by the "
                 "tracking number and the '%(lang)s' sequence will be replaced"
                 " by the language code (en, fr, de)")
    }
