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

FORMAT = '%(asctime)s --  %(message)s'
logging.basicConfig(filename='quants.log',level=logging.INFO, format=FORMAT)

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
    locations_and_products = defaultdict(list)
    sql = """Select distinct stock_quant.location_id, product_id FROM stock_quant
    JOIN stock_location
        ON (stock_quant.location_id = stock_location.id)
    WHERE stock_location.company_id = %s
       AND product_id in (

SELECT product_id
    FROM stock_quant JOIN stock_location
    ON (stock_quant.location_id = stock_location.id)
      WHERE product_id = ANY (
        SELECT distinct product_id from stock_quant
            JOIN stock_location ON (stock_quant.location_id = stock_location.id)
                WHERE stock_location.company_id = %s
                AND qty < 0
      )
      AND stock_location.company_id = %s
      AND stock_location.active = true
      GROUP BY product_id
        HAVING sum(qty) = 0
          AND count(*) > 1)"""

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cr:
        cr.execute(sql, (company_id, company_id, company_id))
        for row in cr.fetchall():
            locations_and_products[row['location_id']].append(row['product_id'])
    return locations_and_products


def clean_inventory_lines(conn, inventory_id, product_ids):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cr:
        logging.info('Deleting correct inventory lines')
        sql = """Delete FROM stock_inventory_line WHERE inventory_id = %s
                    AND product_id not in %s"""
        cr.execute(sql, (inventory_id, tuple(product_ids)))
        conn.commit()


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
        cli.env.context['active_test'] = False
        company_id = cli.env.user.company_id.id
        stock_to_fix = get_faulty_locations_and_products(conn, company_id)
        Inventory = cli.env['stock.inventory']
        Location = cli.env['stock.location']
        logging.info('Removing in process inventory')
        in_progress_inv_ids = Inventory.search([('state', '=', 'confirm')])
        Inventory.unlink(in_progress_inv_ids)
        for location_id, product_ids in stock_to_fix.iteritems():
            location = Location.browse(location_id)
            logging.info(u"Creating inventory for location {}".format(
                location.name.encode('ascii', 'replace')))
            inv_id = Inventory.create({
                'name': u"Corr. quants negatifs pour {}".format(location.name),
                'location_id': location_id,
                'filter': 'none',
                'company_id': company_id,
            })
            inv = Inventory.browse(inv_id)
            inv.prepare_inventory()
            inv = Inventory.browse(inv_id)
            clean_inventory_lines(conn, inv_id, product_ids)
            inv = Inventory.browse(inv_id)
            inv.reset_real_qty()
            inv.action_done()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--env', choices=['dev', 'integration', 'prod'], required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    fix_stock(config)
