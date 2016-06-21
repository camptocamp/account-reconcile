# -*- coding: utf-8 -*-
# © 2013-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import netsvc
from openerp import _, api, fields, models
from openerp.addons.base.res.res_partner import _lang_get
import logging

from postlogistics.web_service import PostlogisticsWebServiceQoQa

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    """ Add a number of products field to allow search on it.

    This in order to group picking of a single offer to set other
    shipping options.

    For exemple: Sending a pair of shoes will be in a small pack and
    sending two pair of shoes will be in a big pack and we want to
    change the shipping label options of all those pack. Thus we want
    a filter that allows us to do that.
    """
    _inherit = "stock.picking"

    number_of_products = fields.Integer(
        compute='_compute_number_of_products',
        string='Number of products',
        store=True
    )

    lang = fields.Selection(
        related='partner_id.lang',
        string='Language',
        selection=_lang_get,
        readonly=True,
        store=True
    )

    active = fields.Boolean(
        'Active', default=True,
        help="The active field allows you to hide the picking without "
             "removing it."
    )

    @api.depends('move_lines', 'move_lines.product_qty')
    def _compute_number_of_products(self):
        for picking in self:
            picking.number_of_products = sum(
                picking.mapped('move_lines.product_qty')
            )

    def _generate_postlogistics_label(self, webservice_class=None,
                                      package_ids=None):
        """ Generate post label using QoQa specific to hide parent name in  """

        return super(StockPicking, self)._generate_postlogistics_label(
            webservice_class=PostlogisticsWebServiceQoQa,
            package_ids=package_ids
        )

    # TODO: Et en V9 :) ?
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
                                 if m.state in ('cancel', 'done') or
                                 move_product_qty[m.id] != 0]
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

    # TODO: plus de workflow, a reproduire ?
    def test_finished(self, cursor, user, ids):
        wf_service = netsvc.LocalService("workflow")
        res = super(stock_picking, self).test_finished(cursor, user, ids)
        for picking in self.browse(cursor, user, ids):
            for move in picking.move_lines:
                if move.state in('done', 'cancel') and move.procurements:
                    for procurement in move.procurements:
                        wf_service.trg_validate(user, 'procurement.order',
                                                procurement.id,
                                                'button_check', cursor)
        return res

    def test_cancel(self, cursor, user, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        res = super(stock_picking, self).test_cancel(cursor, user, ids,
                                                     context=context)
        for picking in self.browse(cursor, user, ids, context=context):
            for move in picking.move_lines:
                if move.state == 'cancel' and move.procurements:
                    for procurement in move.procurements:
                        wf_service.trg_validate(user, 'procurement.order',
                                                procurement.id,
                                                'button_check', cursor)
        return res


class StockMove(models.Model):

    _inherit = 'stock.move'

    # TODO: ?
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
                             if m.state in ('cancel', 'done') or
                             move_product_qty[m.id] != 0]
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

    # TODO: ?
    # Until base upgrade : this calls the correct workflow
    # on the stock pickings when moves are cancelled
    # (either transferred or cancelled)
    def action_cancel(self, cr, uid, ids, context=None):
        if not len(ids):
            return True
        if context is None:
            context = {}
        pickings = set()
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('confirmed', 'waiting', 'assigned', 'draft'):
                if move.picking_id:
                    pickings.add(move.picking_id.id)
            if move.move_dest_id and move.move_dest_id.state == 'waiting':
                self.write(cr, uid, [move.move_dest_id.id],
                           {'state': 'confirmed'}, context=context)
                if context.get('call_unlink', False) and \
                        move.move_dest_id.picking_id:
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_write(uid, 'stock.picking',
                                         move.move_dest_id.picking_id.id, cr)
        self.write(cr, uid, ids, {'state': 'cancel', 'move_dest_id': False},
                   context=context)
        if not context.get('call_unlink', False):
            for pick in self.pool.get('stock.picking').browse(
                    cr, uid, list(pickings), context=context):
                if all(move.state == 'cancel' for move in pick.move_lines):
                    self.pool.get('stock.picking').write(cr, uid, [pick.id],
                                                         {'state': 'cancel'},
                                                         context=context)

        wf_service = netsvc.LocalService("workflow")
        if context.get('picking_trg_write', True):
            for pick_id in pickings:
                wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
        return True
