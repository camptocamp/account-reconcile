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
from openerp import netsvc
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.addons.base.res.res_partner import _lang_get

from postlogistics.web_service import PostlogisticsWebServiceQoQa


class stock_picking(orm.Model):
    """ Add a number of products field to allow search on it.

    This in order to group picking of a single offer to set other
    shipping options.

    For exemple: Sending a pair of shoes will be in a small pack and
    sending two pair of shoes will be in a big pack and we want to
    change the shipping label options of all those pack. Thus we want
    a filter that allows us to do that.

    """
    _inherit = "stock.picking"

    def _get_number_of_products(self, cr, uid, ids, field_names,
                                arg=None, context=None):
        result = {}
        for picking in self.browse(cr, uid, ids, context=context):
            number_of_products = 0
            for line in picking.move_lines:
                number_of_products += line.product_qty
            result[picking.id] = number_of_products
        return result

    def _get_picking(self, cr, uid, ids, context=None):
        result = set()
        move_obj = self.pool.get('stock.move')
        for line in move_obj.browse(cr, uid, ids, context=context):
            result.add(line.picking_id.id)
        return list(result)

    def _get_from_partner(self, cr, uid, ids, context=None):
        return self.search(cr, uid, [('partner_id', 'in', ids)],
                           context=context)

    def _get_from_partner_fn(self, cr, uid, ids, context=None):
        """ Do not modify. Let `_get_from_partner` be inheritable. """
        return self.pool['stock.picking']._get_from_partner(cr, uid, ids,
                                                            context=context)

    _columns = {
        'number_of_products': fields.function(
            _get_number_of_products,
            type='integer', string='Number of products',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c=None: ids,
                                  ['move_lines'], 10),
                'stock.move': (_get_picking, ['product_qty'], 10),
            }),
        'lang': fields.related('partner_id', 'lang',
                               string='Language',
                               type='selection',
                               selection=_lang_get,
                               readonly=True,
                               store={
                                   'stock.picking': (
                                       lambda self, cr, uid, ids, c=None: ids,
                                       ['partner_id'], 20),
                                   'res.partner': (_get_from_partner_fn,
                                                   ['lang'], 20)
                               }),
    }

    def _generate_postlogistics_label(self, cr, uid, picking,
                                      webservice_class=None,
                                      tracking_ids=None, context=None):
        """ Generate post label using QoQa specific to hide parent name in  """
        return super(stock_picking, self)._generate_postlogistics_label(
            cr, uid, picking,
            webservice_class=PostlogisticsWebServiceQoQa,
            tracking_ids=tracking_ids,
            context=context)

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        # Wonderful overwrite of big mega hyper monolithic method do_partial
        # we want here that partial delivery keeps packs in case no product
        # of a pack were sent. Thus the pack was not used
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        pricetype_obj = self.pool.get('product.price.type')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            (move_product_qty, prodlot_ids, product_avail,
             partial_qty, product_uoms) = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s' % move.id, {})
                product_qty = partial_data.get('product_qty', 0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', False)
                product_price = partial_data.get('product_price', 0.0)
                product_currency = partial_data.get('product_currency', False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(
                    cr, uid, product_uoms[move.id],
                    product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in' and
                        move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom,
                                               product_qty,
                                               product.uom_id.id)
                    price_type_id = pricetype_obj.search(
                        cr, uid,
                        [('field', '=', 'standard_price')],
                        context=context)[0]
                    price_type = pricetype_obj.browse(cr, uid,
                                                      price_type_id,
                                                      context=context)
                    price_type_currency_id = price_type.currency_id.id

                    if product.id not in product_avail:
                        # keep track of stock on hand including
                        # processed lines not yet marked as done
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        # New price in company currency
                        new_price = currency_obj.compute(
                            cr, uid, product_currency,
                            move_currency_id, product_price, round=False)
                        new_price = uom_obj._compute_price(
                            cr, uid, product_uom, new_price, product.uom_id.id)
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            price_get = product.price_get('standard_price',
                                                          context=context)
                            amount_unit = price_get[product.id]
                            # Here we must convert the new price
                            # computed in the currency of the price_type
                            # of the product (e.g. company currency:
                            # EUR, price_type: USD) The current value is
                            # still in company currency at this stage
                            new_std_price = (
                                (amount_unit * product_avail[product.id]) +
                                (new_price * qty)
                            ) / (product_avail[product.id] + qty)
                        # Convert the price in price_type currency
                        new_std_price = currency_obj.compute(
                            cr, uid, move_currency_id,
                            price_type_currency_id, new_std_price)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id],
                                          {'standard_price': new_std_price},
                                          context=context)

                        # Record the values that were chosen in the
                        # wizard, so they can be used for inventory
                        # valuation if real-time valuation is enabled.
                        move_obj.write(
                            cr, uid, [move.id],
                            {'price_unit': product_price,
                             'price_currency_id': product_currency},
                            context=context)

                        product_avail[product.id] += qty

            ###################################################################
            # Start change 1/2
            # list all tracking_id with at least one move to pick partially
            # this give us the tracking that cannot be reused
            used_tracking_ids = [m.tracking_id.id for m in pick.move_lines
                                 if m.state in ('cancel', 'done')
                                 or move_product_qty[m.id] != 0]
            # End change 1/2
            ###################################################################

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking_name = pick.name
                    seq_next = sequence_obj.get(cr, uid,
                                                'stock.picking.%s' % pick.type)
                    self.write(cr, uid, [pick.id],
                               {'name': seq_next},
                               context=context)
                    new_picking = self.copy(
                        cr, uid, pick.id,
                        {'name': new_picking_name,
                         'move_lines': [],
                         'state': 'draft',
                         }, context=context)
                if product_qty:
                    defaults = {
                        'product_qty': product_qty,
                        # TODO: put correct uos_qty
                        'product_uos_qty': product_qty,
                        'picking_id': new_picking,
                        'state': 'assigned',
                        'move_dest_id': move.move_dest_id.id,
                        'price_unit': move.price_unit,
                        'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                ###############################################################
                # Start change 2/2
                values = {
                    'product_qty': move.product_qty - partial_qty[move.id],
                    # TODO: put correct uos_qty
                    'product_uos_qty': move.product_qty - partial_qty[move.id],
                    'prodlot_id': False,
                }
                # erase tracking_id only if this one has already been used
                if move.tracking_id.id in used_tracking_ids:
                    values['tracking_id'] = False
                move_obj.write(cr, uid, [move.id], values)
                # End change 2/2
                ###############################################################

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete],
                               {'picking_id': new_picking},
                               context=context)
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id],
                            'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty': product_qty,
                    # TODO: put correct uos_qty
                    'product_uos_qty': product_qty,
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking',
                                        new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context=context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking,
                                        'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = pick.id
                back_order_name = self.browse(cr, uid,
                                              delivered_pack_id,
                                              context=context).name
                message = _("Back order <em>%s</em> has been "
                            "<b>created</b>.") % back_order_name
                self.message_post(cr, uid, new_picking, body=message,
                                  context=context)
            else:
                self.action_move(cr, uid, [pick.id], context=context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id,
                                        'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id,
                                         context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res


class stock_picking_in(orm.Model):
    """ Add a number of products field to allow search on it.

    This in order to group picking of a single offer to set other
    shipping options.

    For exemple: Sending a pair of shoes will be in a small pack and
    sending two pair of shoes will be in a big pack and we want to
    change the shipping label options of all those pack. Thus we want
    a filter that allows us to do that.

    """
    _inherit = "stock.picking.in"

    def _get_number_of_products(self, cr, uid, ids, field_names,
                                arg=None, context=None):
        result = {}
        for picking in self.browse(cr, uid, ids, context=context):
            number_of_products = 0
            for line in picking.move_lines:
                number_of_products += line.product_qty
            result[picking.id] = number_of_products
        return result

    def _get_picking(self, cr, uid, ids, context=None):
        result = set()
        move_obj = self.pool.get('stock.move')
        for line in move_obj.browse(cr, uid, ids, context=context):
            result.add(line.picking_id.id)
        return list(result)

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        return self.pool['stock.picking'].do_partial(
            cr, uid, ids, partial_datas, context=context)

    _columns = {
        'number_of_products': fields.function(
            _get_number_of_products,
            type='integer', string='Number of products',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c=None: ids,
                                  ['move_lines'], 10),
                'stock.move': (_get_picking, ['product_qty'], 10),
            }),
    }


class stock_picking_out(orm.Model):
    """ Add a number of products field to allow search on it.

    This in order to group picking of a single offer to set other
    shipping options.

    For exemple: Sending a pair of shoes will be in a small pack and
    sending two pair of shoes will be in a big pack and we want to
    change the shipping label options of all those pack. Thus we want
    a filter that allows us to do that.

    """
    _inherit = "stock.picking.out"

    def _get_number_of_products(self, cr, uid, ids, field_names,
                                arg=None, context=None):
        result = {}
        for picking in self.browse(cr, uid, ids, context=context):
            number_of_products = 0
            for line in picking.move_lines:
                number_of_products += line.product_qty
            result[picking.id] = number_of_products
        return result

    def _get_picking(self, cr, uid, ids, context=None):
        result = set()
        move_obj = self.pool.get('stock.move')
        for line in move_obj.browse(cr, uid, ids, context=context):
            result.add(line.picking_id.id)
        return list(result)

    def _get_from_partner_fn(self, cr, uid, ids, context=None):
        """ Do not modify. Let `stock_picking._get_from_partner` be
        inheritable. """
        return self.pool['stock.picking']._get_from_partner(cr, uid, ids,
                                                            context=context)

    _columns = {
        'number_of_products': fields.function(
            _get_number_of_products,
            type='integer', string='Number of products',
            store={
                'stock.picking': (lambda self, cr, uid, ids, c=None: ids,
                                  ['move_lines'], 10),
                'stock.move': (_get_picking, ['product_qty'], 10),
            }),
        'lang': fields.related('partner_id', 'lang',
                               string='Language',
                               type='selection',
                               selection=_lang_get,
                               readonly=True,
                               store={
                                   'stock.picking.out': (
                                       lambda self, cr, uid, ids, c=None: ids,
                                       ['partner_id'], 20),
                                   'res.partner': (_get_from_partner_fn,
                                                   ['lang'], 20)
                               }),
    }

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        return self.pool['stock.picking'].do_partial(
            cr, uid, ids, partial_datas, context=context)


class stock_move(orm.Model):

    _inherit = 'stock.move'

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        # Wonderful overwrite of big mega hyper monolithic method do_partial
        # we want here that partial delivery keeps packs in case no product
        # of a pack were sent. Thus the pack was not used
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        pricetype_obj = self.pool.get('product.price.type')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        #######################################################################
        # Start change 1/3
        all_moves = self.browse(cr, uid, ids, context=context)
        for move in all_moves:
            # End change 1/3
            ###################################################################
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s' % (move.id), False)
            assert partial_data, _('Missing partial picking data '
                                   'for move #%s.') % (move.id)
            product_qty = partial_data.get('product_qty', 0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom', False)
            product_price = partial_data.get('product_price', 0.0)
            product_currency = partial_data.get('product_currency', False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            if (move.picking_id.type == 'in' and
                    move.product_id.cost_method == 'average'):
                product = product_obj.browse(cr, uid, move.product_id.id)
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom,
                                           product_qty,
                                           product.uom_id.id)
                price_type_id = pricetype_obj.search(
                    cr, uid,
                    [('field', '=', 'standard_price')],
                    context=context)[0]
                price_type = pricetype_obj.browse(cr, uid,
                                                  price_type_id,
                                                  context=context)
                price_type_currency_id = price_type.currency_id.id
                if qty > 0:
                    new_price = currency_obj.compute(
                        cr, uid, product_currency,
                        move_currency_id, product_price, round=False)
                    new_price = uom_obj._compute_price(cr, uid,
                                                       product_uom, new_price,
                                                       product.uom_id.id)
                    if product.qty_available <= 0:
                        new_std_price = new_price
                    else:
                        # Get the standard price
                        price_get = product.price_get('standard_price',
                                                      context=context)
                        amount_unit = price_get[product.id]
                        # Here we must convert the new price computed in
                        # the currency of the price_type of the product
                        # (e.g. company currency: EUR, price_type: USD)
                        # The current value is still in company currency
                        # at this stage
                        new_std_price = (
                            (amount_unit * product.qty_available) +
                            (new_price * qty)
                        ) / (product.qty_available + qty)
                    # Convert the price in price_type currency
                    new_std_price = currency_obj.compute(
                        cr, uid, move_currency_id,
                        price_type_currency_id, new_std_price)
                    # Write the field according to price type field
                    product_obj.write(cr, uid,
                                      [product.id],
                                      {'standard_price': new_std_price},
                                      context=context)

                    # Record the values that were chosen in the wizard,
                    # so they can be used for inventory valuation if
                    # real-time valuation is enabled.
                    self.write(cr, uid, [move.id],
                               {'price_unit': product_price,
                                'price_currency_id': product_currency,
                                }, context=context)

        #######################################################################
        # Start change 2/3
        # list all tracking_id with at least one move to pick partially
        # this give us the tracking that cannot be reused
        used_tracking_ids = [m.tracking_id.id for m in all_moves
                             if m.state in ('cancel', 'done')
                             or move_product_qty[m.id] != 0]
        # End change 2/3
        #######################################################################
        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {
                    'product_qty': product_qty,
                    'product_uos_qty': product_qty,
                    'picking_id': move.picking_id.id,
                    'state': 'assigned',
                    'move_dest_id': move.move_dest_id.id,
                    'price_unit': move.price_unit,
                }
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            ###################################################################
            # Start change 3/3
            values = {'product_qty': move.product_qty - product_qty,
                      'product_uos_qty': move.product_qty - product_qty,
                      'prodlot_id': False,
                      }
            # erase tracking_id only if this one has already been used
            if move.tracking_id.id in used_tracking_ids:
                values['tracking_id'] = False
            self.write(cr, uid, [move.id], values)
            # End change 3/3
            ###################################################################

        for move in too_many:
            self.write(
                cr, uid, [move.id],
                {'product_qty': move.product_qty,
                 'product_uos_qty': move.product_qty,
                 },
                context=context)
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id],
                           {'prodlot_id': prodlot_ids.get(move.id)},
                           context=context)
            self.action_done(cr, uid, [move.id], context=context)
            if move.picking_id.id:
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move
                    ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""",
                           ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking',
                                            move.picking_id.id,
                                            'button_done', cr)

        return [move.id for move in complete]
