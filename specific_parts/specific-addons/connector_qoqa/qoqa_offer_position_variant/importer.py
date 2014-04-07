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

from openerp.addons.connector.unit.mapper import (backend_to_m2o,
                                                  ImportMapper,
                                                  ImportMapChild
                                                  )
from ..backend import qoqa


@qoqa
class QoQaOfferPositionVariantImportMapper(ImportMapper):
    _model_name = 'qoqa.offer.position.variant'

    direct = [('quantity', 'quantity'),
              (backend_to_m2o('variation_id', binding='qoqa.product.product'),
               'product_id'),
              ('sorting_weight', 'sequence'),
              ('id', 'qoqa_id'),
              ]


@qoqa
class LineMapChild(ImportMapChild):
    _model_name = 'qoqa.offer.position.variant'

    def get_item_values(self, map_record, to_attr, options):
        values = map_record.values(**options)
        binder = self.get_binder_for_model()
        binding_id = binder.to_openerp(map_record.source['id'])
        if binding_id is not None:
            # already exists, keeps the id
            values['binding_id'] = binding_id
        return values

    def format_items(self, items_values):
        # if we already have an ID (found in get_item_values())
        # we change the command to update the existing record
        items = []
        for item in items_values[:]:
            if item.get('binding_id'):
                binding_id = item.pop('binding_id')
                # update the record
                items.append((1, binding_id, item))
            else:
                # create the record
                items.append((0, 0, item))
        return items
