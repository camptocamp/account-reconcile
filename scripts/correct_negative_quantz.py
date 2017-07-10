#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from collections import defaultdict
import logging
import argparse
import ConfigParser
import odoorpc
import psycopg2
import psycopg2.extras

logging.basicConfig(level=logging.INFO)

ADMIN_USERS = ('admin_ch', 'admin_fr')


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
    return odoorpc.ODOO(config['host'],
                        protocol=config['protocol'],
                        port=config['port'],
                        timeout=None)


def db_conn(config):
    """Return a db connection based on config dict"""
    return psycopg2.connect(config['dsn'])


def get_faulty_locations_and_products(conn, company_id):
    """Get all products and stock locations pair that have
    negative quants and an available qty that is 0.
    The pair are filtered by company"""
    sql = """SELECT sum(qty) AS cmp_qty, product_id, stock_quant.location_id
    FROM stock_quant JOIN stock_location
    ON (stock_quant.location_id = stock_location.id)
      WHERE product_id = ANY (select distinct product_id from stock_quant where qty < 0)
      AND stock_location.company_id = %s
      AND stock_location.active = true
      GROUP BY product_id, stock_quant.location_id
        HAVING sum(qty) = 0"""
    locations_and_products = defaultdict(list)
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cr:
        cr.execute(sql, (company_id,))
        for row in cr.fetchall():
            locations_and_products[row['location_id']].append(row['product_id'])
    return locations_and_products


def fix_stock(config):
    """Fix negative quants on product
    by creating inventory for association of:
    - company
    - location
    - product
    """

    conn = db_conn(config)
    cli = rpc_client(config)
    for user in ADMIN_USERS:
        cli.login(config['db'], user, config[user])
        company_id = cli.env.user.company_id.id
        stock_to_fix = get_faulty_locations_and_products(conn, company_id)
        Inventory = cli.env['stock.inventory']
        Location = cli.env['stock.location']
        for location_id, product_ids in stock_to_fix.iteritems():
            location = Location.browse(location_id)
            logging.info("Creating inventory for location {}".format(location.display_name))
            inv_id = Inventory.create({
                'name': "Corr. quants negatifs pour {}".format(location.name),
                'location_id': location_id,
                'filter': 'none',
                'company_id': company_id,
            })
            inv = Inventory.browse(inv_id)
            inv.prepare_inventory()
            inv = Inventory.browse(inv_id)
            for inv_line in inv.line_ids:
                if inv_line.product_id.id not in product_ids:
                    inv_line.unlink()
            inv.reset_real_qty()
            inv.action_done()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--env', choices=['dev', 'integration', 'prod'], required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    fix_stock(config)
