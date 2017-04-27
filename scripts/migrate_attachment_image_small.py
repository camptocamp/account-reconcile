#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse

import odoorpc

parser = argparse.ArgumentParser()
parser.add_argument('--env', choices=['integration', 'prod'], required=True)
parser.add_argument('--password', type=str, required=True)

args = parser.parse_args()

env = args.env
password = args.password


def get_config(env):
    config = {
        'integration': {
            'host': 'erp-integration.qoqa.ninja',
            'db': 'qoqa_odoo_integration',
        },
        'prod': {
            'host': 'erp.qoqa.ninja',
            'db': 'qoqa_odoo_prod',
        },
    }
    return config[env]


config = get_config(env)

client = odoorpc.ODOO(config['host'],
                      protocol='jsonrpc+ssl', port=443,
                      timeout=None)
client.login(config['db'], 'admin', password)

client.env['ir.attachment'].migrate_small_attachments_from_s3_to_db()
