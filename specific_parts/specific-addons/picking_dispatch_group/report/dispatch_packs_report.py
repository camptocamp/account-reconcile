# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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
import time
from datetime import date
from operator import attrgetter
from itertools import groupby
from report import report_sxw


class PrintDispatchPacks(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(PrintDispatchPacks, self).__init__(cr, uid, name,
                                                 context=context)
        self.localcontext.update({
            'time': time,
            'date': date,
            'cr': cr,
            'uid': uid,
            'get_packs': self._get_packs,
        })

    def _get_packs(self, dispatch):
        moves = sorted(dispatch.move_ids, key=attrgetter('tracking_id.name'))
        for pack, moves in groupby(moves, key=attrgetter('tracking_id')):
            yield pack, list(moves)


report_sxw.report_sxw('report.webkit.dispatch_packs',
                      'picking.dispatch',
                      'addons/picking_dispatch_group/report/dispatch_packs.html.mako',
                      parser=PrintDispatchPacks)
