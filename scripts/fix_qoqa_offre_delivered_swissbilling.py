# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import odoorpc
import math

##


def get_config(path, env):
    """Returns a config dict for a given env"""
    config = ConfigParser.ConfigParser()
    with open(path) as config_file:
        config.readfp(config_file)
        if config.has_section(env):
            return dict(config.items(env))
        else:
            raise ValueError('Unknown env {}'.format(env))


def rpc_client(config):
    """Return a rpc client based on config dict"""
    client = odoorpc.ODOO(config['host'],
                          protocol=config['protocol'],
                          port=config['port'],
                          timeout=None)
    client.login(config['database'],
                 config['erp_user'],
                 config['erp_pwd'])
    return client

def float_check_precision(precision_digits=None, precision_rounding=None):
    assert (precision_digits is not None or precision_rounding is not None) and \
        not (precision_digits and precision_rounding),\
         "exactly one of precision_digits and precision_rounding must be specified"
    if precision_digits is not None:
        return 10 ** -precision_digits
    return precision_rounding

def float_round(value, precision_digits=None, precision_rounding=None, rounding_method='HALF-UP'):
    """Return ``value`` rounded to ``precision_digits`` decimal digits,
       minimizing IEEE-754 floating point representation errors, and applying
       the tie-breaking rule selected with ``rounding_method``, by default
       HALF-UP (away from zero).
       Precision must be given by ``precision_digits`` or ``precision_rounding``,
       not both!

       :param float value: the value to round
       :param int precision_digits: number of fractional digits to round to.
       :param float precision_rounding: decimal number representing the minimum
           non-zero value at the desired precision (for example, 0.01 for a
           2-digit precision).
       :param rounding_method: the rounding method used: 'HALF-UP' or 'UP', the first
           one rounding up to the closest number with the rule that number>=0.5 is
           rounded up to 1, and the latest one always rounding up.
       :return: rounded float
    """
    rounding_factor = float_check_precision(precision_digits=precision_digits,
                                             precision_rounding=precision_rounding)
    if rounding_factor == 0 or value == 0: return 0.0

    # NORMALIZE - ROUND - DENORMALIZE
    # In order to easily support rounding to arbitrary 'steps' (e.g. coin values),
    # we normalize the value before rounding it as an integer, and de-normalize
    # after rounding: e.g. float_round(1.3, precision_rounding=.5) == 1.5

    # TIE-BREAKING: HALF-UP (for normal rounding)
    # We want to apply HALF-UP tie-breaking rules, i.e. 0.5 rounds away from 0.
    # Due to IEE754 float/double representation limits, the approximation of the
    # real value may be slightly below the tie limit, resulting in an error of
    # 1 unit in the last place (ulp) after rounding.
    # For example 2.675 == 2.6749999999999998.
    # To correct this, we add a very small epsilon value, scaled to the
    # the order of magnitude of the value, to tip the tie-break in the right
    # direction.
    # Credit: discussion with OpenERP community members on bug 882036

    normalized_value = value / rounding_factor # normalize
    epsilon_magnitude = math.log(abs(normalized_value), 2)
    epsilon = 2**(epsilon_magnitude-53)
    if rounding_method == 'HALF-UP':
        normalized_value += cmp(normalized_value,0) * epsilon
        rounded_value = round(normalized_value) # round to integer

    # TIE-BREAKING: UP (for ceiling operations)
    # When rounding the value up, we instead subtract the epsilon value
    # as the the approximation of the real value may be slightly *above* the
    # tie limit, this would result in incorrectly rounding up to the next number
    # The math.ceil operation is applied on the absolute value in order to
    # round "away from zero" and not "towards infinity", then the sign is
    # restored.

    elif rounding_method == 'UP':
        sign = cmp(normalized_value, 0)
        normalized_value -= sign*epsilon
        rounded_value = math.ceil(abs(normalized_value))*sign # ceil to integer

    result = rounded_value * rounding_factor # de-normalize
    return result


def compute_qty_obj(from_unit, qty, to_unit, round=True, rounding_method='UP', context=None):
        if context is None:
            context = {}
        if from_unit.category_id.id != to_unit.category_id.id:
            if context.get('raise-exception', True):
                raise 'Conversion from Product UoM %s to Default UoM %s is not possible as they both belong to different Category!.'
            else:
                return qty
        amount = qty/from_unit.factor
        if to_unit:
            amount = amount * to_unit.factor
            if round:
                amount = float_round(amount, precision_rounding=to_unit.rounding, rounding_method=rounding_method)
        return amount


def get_delivered_qty(line, odoo):
        """Computes the delivered quantity on sale order lines, based on done stock moves related to its procurements
        """
        # Get all procurement move
        move_tab =[]
        for procurement in line.procurement_ids:
            move_tab += [x for x in procurement.move_ids]
        qty = 0.0
        for move in move_tab:
            #Note that we don't decrease quantity for customer returns on purpose: these are exeptions that must be treated manually. Indeed,
            #modifying automatically the delivered quantity may trigger an automatic reinvoicing (refund) of the SO, which is definitively not wanted
            if move.state == 'done' and move.location_dest_id.usage == "customer":
                if not move.origin_returned_move_id:
                    qty += compute_qty_obj(move.product_uom, move.product_uom_qty, line.product_uom)
        return qty


def fix_sale_order_swissbilling(picking_domain=[],to_add_order=[], config=False):
    odoo = rpc_client(config)
    # We reconpute all refund
    SaleOrder = odoo.env['sale.order']
    Picking = odoo.env['stock.picking']
    print "Search Orders"
    all_sale_orders_ids = SaleOrder.search([('payment_mode_id','=',15),('state','not in',['done','cancel'])])
    picking_domain += [('sale_id','in',all_sale_orders_ids)]
    print "Search restricted order"
    all_picking_ids = Picking.search(picking_domain)
    print "Get all picking"
    all_sale_ids = []
    cpt = 1
    print "Length %s" % (len(all_picking_ids))
    for picking_id in all_picking_ids:
        try:
            all_sale_ids.append(Picking.browse(picking_id).sale_id.id)
        except:
            print picking_id
        cpt += 1
    # due to lsit index out of rang on some picking
    # I have add the sale order related manually
    all_sale_ids += to_add_order
    print "Filter sale order"
    cpt = 1
    len_sale_orders = len(all_sale_ids)
    #  account_id
    #   id  | code
    # ------+-------
    #   576 | 32000
    #  2702 | 32001
    #  2706 | 32005
    rewrite_offer = []
    for sale_order_id in all_sale_ids:
        sale_order = SaleOrder.browse(sale_order_id)
        print "%s - %s - %s - %s - %s" % (cpt, len_sale_orders , sale_order.id, sale_order.state, sale_order.date_order)
        for line in sale_order.order_line:
            # Get the procurement related to this sale order line
            delivered_qty = get_delivered_qty(line, odoo)
            print '%s - %s' % (delivered_qty, line.qty_delivered)
            if delivered_qty != line.qty_delivered:
                if sale_order.state == 'done':
                    # Cela devrait jamais arrivé mais
                    print str("Rewrite state")
                    sale_order.write({'state': 'sale'})
                print str("Rewrite QTY")
                rewrite_offer.append(sale_order.id)
                line.write({'qty_delivered': delivered_qty})
        cpt += 1
    print "Order Rewrite : %s" % (rewrite_offer,)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--env',
                        choices=['dev', 'integration', 'prod'], required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    #fix_sale_order_swissbilling(order_domain=[('date_order', '>=', '2017-07-21'),('payment_mode_id','=',15)],config=config)
    #fix_sale_order_swissbilling(picking_domain=[('date_done','>=',3717307)],config=config)
    #fix_sale_order_swissbilling(picking_domain=[('date_done','>=','2017-07-21')],to_add_order=[3718126,3721095,3728866],config=config)
    fix_sale_order_swissbilling(picking_domain=[('origin','=','04005433')],to_add_order=[],config=config)
