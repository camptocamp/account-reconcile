# -*- coding: utf-8 -*-
# Copyright 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from openerp.osv import orm


class stock_location(orm.Model):
    _inherit = "stock.location"

    def _product_get_report(self, cr, uid, ids, product_ids=False,
                            context=None, recursive=False):
        """ Ugly copy of _product_get_report to overwrite it to simply
        add description_warehouse.

        This because result['product'] is a list without product id.
        Thus it makes thing really difficult to match product with their
        description_warehouse
        @param product_ids: Ids of product
        @param recursive: True or False
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        product_obj = self.pool['product.product']
        # Take the user company and pricetype
        user_obj = self.pool['res.users']
        user = user_obj.browse(cr, uid, uid, context=context)
        context['currency_id'] = user.company_id.currency_id.id

        # To be able to offer recursive or non-recursive reports we need
        # to prevent recursive quantities by default
        context['compute_child'] = False

        if not product_ids:
            product_ids = product_obj.search(cr, uid, [],
                                             context={'active_test': False})

        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_by_uom = {}
        products_by_id = {}
        for product in products:
            products_by_uom.setdefault(product.uom_id.id, [])
            products_by_uom[product.uom_id.id].append(product)
            products_by_id.setdefault(product.id, [])
            products_by_id[product.id] = product

        result = {}
        result['product'] = []
        for id in ids:
            quantity_total = 0.0
            total_price = 0.0
            for uom_id in products_by_uom.keys():
                fnc = self._product_get
                if recursive:
                    fnc = self._product_all_get
                ctx = context.copy()
                ctx['uom'] = uom_id
                qty = fnc(cr, uid, id, [x.id for x in products_by_uom[uom_id]],
                          context=ctx)
                for product_id in qty.keys():
                    if not qty[product_id]:
                        continue
                    product = products_by_id[product_id]
                    quantity_total += qty[product_id]

                    # Compute based on pricetype
                    # Choose the right filed standard_price to read
                    price_get = product.price_get('standard_price',
                                                  context=context)
                    amount_unit = price_get[product.id]
                    price = qty[product_id] * amount_unit

                    total_price += price
                    result['product'].append({
                        'price': amount_unit,
                        'prod_name': product.name,
                        # used by lot_overview_all report!
                        'code': product.default_code,
                        'variants': product.variants or '',
                        'uom': product.uom_id.name,
                        'prod_qty': qty[product_id],
                        'price_value': price,
                        #######################################################
                        # Start of change 1/1
                        'description_warehouse': product.description_warehouse,
                        # End of change 1/1
                        #######################################################
                    })
        result['total'] = quantity_total
        result['total_price'] = total_price
        return result
