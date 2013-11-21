# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
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

from openerp.addons.connector.unit.mapper import ExportMapper
from ..backend import qoqa
from ..unit.mapper import m2o_to_backend


@qoqa
class OfferPositionVariantExportMapper(ExportMapper):
    """ Called from the qoqa.offer.position's mapper """
    _model_name = 'qoqa.offer.position.variant'

    direct = [(m2o_to_backend('product_id', binding='qoqa.product.template'),
               'product_id'),
              ('quantity', 'quantity'),
              ]
