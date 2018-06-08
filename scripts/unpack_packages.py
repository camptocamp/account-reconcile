#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import argparse
import ConfigParser

import odoorpc

LOCATIONS = {
    "Stock": "stock.stock_location_stock",
    "Controler": "__export__.stock_location_211",
    "SAV": "scenario.location_ch_sav",
}
BATCH_SIZE = 100 


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
    connection = odoorpc.ODOO(
        config['host'],
        protocol=config['protocol'],
        port=config['port'],
        timeout=None,
    )
    connection.login(config['db'], 'admin_ch', config['admin_ch'])
    return connection


def get_child_locations(location):
    location_ids = [location.id]
    for child_loc in location.child_ids:
        location_ids.extend(get_child_locations(child_loc))
    return location_ids


def get_batched_packages(cli, package_ids):
    packages = cli.env["stock.quant.package"].browse(package_ids)
    batches = len(packages) // BATCH_SIZE
    for index in xrange(batches + 1):
        yield packages[BATCH_SIZE * index:BATCH_SIZE * (index + 1)]


def unpack_packages(config):
    cli = rpc_client(config)
    location_ids = []
    for location in LOCATIONS.values():
        location_id = cli.env.ref(location)
        location_ids.extend(get_child_locations(location_id))
    packages = cli.env["stock.quant.package"].search([
        ('location_id', 'in', location_ids),
    ])
    for package_batch in get_batched_packages(cli, packages):
        package_batch.unpack()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', choices=['dev', 'integration', 'prod'], required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    unpack_packages(config)
