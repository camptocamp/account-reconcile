#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import argparse
import ConfigParser
import odoorpc
import psycopg2
import psycopg2.extras

logging.basicConfig(filename='quants.log', level=logging.INFO)

ADMIN_USERS = ('admin_ch', 'admin_fr')

SO_LIST = [
    '3399162',
    '3397044',
    '3334543',
    '3334553',
    '3333997',
    '3333521',
    '3332829',
    '3333068',
    '3332453',
    '3332389',
    '3331908',
    '3331717',
    '3331857',
    '3331478',
    '3325624',
    '3325466',
    '3325400',
    '3322952',
    '3322156',
    '3320449',
    '3319571',
    '3319276',
    '3318832',
    '3318477',
    '3317480',
    '3315757',
    '3314805',
    '3314856',
    '3314568',
    '3314034',
    '3313820',
    '3313648',
    '3313417',
    '2730536',
    '2730464',
    '2730153',
    '2729932',
    '2693355',
    '2690371',
    '2690231',
    '2611179',
    '2611163',
    '2611089',
    '2546222',
    '2545796',
    '2545673',
    '2545671',
    '2545639',
    '2544784',
    '2544548',
    '2544593',
    '2544564',
    '2450058',
    '2332965',
    '2332037',
    '2331837',
    '2330349',
    '2328316',
    '2330095',
    '2328207',
    '2235324',
    '2229969',
    '2229500',
    '2229322',
    '2229278',
    '2229154',
    '2227854',
    '2227718',
    '2227468',
    '2227209',
    '2227191',
    '2226910',
    '2201681',
    '2183404',
    '2169797',
    '2169713',
    '2169506',
    '2169472',
    '2169107',
    '2169102',
    '2168918',
    '2146560',
    '2146190',
    '2146038',
    '2145821',
    '2145714',
    '2145650',
    '2145454',
    '2145292',
    '2145225',
    '2145210',
    '2145031',
    '2140485',
    '2140509',
    '2140219',
    '2140229',
    '2140137',
    '2137623',
    '2139912',
    '2139739',
    '2139433',
    '2138634',
    '2137929',
    '2137846',
    '2137339',
    '2137334',
    '2137307',
    '2096554',
    '2096487',
    '2095502',
    '2095062',
    '2094961',
    '2094929',
    '2073157',
    '2022000',
    '2021997',
    '1983463',
    '1983244',
    '1982410',
    '1982389',
    '1982355',
    '1982291',
    '1970929',
    '1970462',
    '1970074',
    '1969747',
    '1969264',
    '1969020',
    '1921213',
    '1920867',
    '1920324',
    '1919173',
    '1918165',
    '1918359',
    '1918302',
    '1802154',
    '1791972',
    '1791641',
    '1718393',
    '1718231',
    '1718067',
    '1717842',
    '1717419',
    '1717137',
    '1717088',
    '1717008',
]


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


def fix_reconcile(config):

    # conn = db_conn(config)
    cli = rpc_client(config)
    for user in ADMIN_USERS:
        cli.login(config['db'], user, config[user])
        cli.env.context['active_test'] = False

        # Select & remove reconcile on account.move.line from SO_LIST
        SaleOrder = cli.env['sale.order']
        sale_order_ids = SaleOrder.browse(SO_LIST)
        AccountMassReconcile = cli.env['account.mass.reconcile']

        logging.info('Unreconcile account.move.lines')

        for sale_order in sale_order_ids:
            for invoice in sale_order.invoice_ids:
                if invoice.move_id:
                    for move_line in invoice.move_id.line_ids:
                        move_line.remove_move_reconcile()

        # Do the reconciliation
        account_ids = cli.env['account.account'].browse()
        account_ids |= cli.env.ref('scenario.pcg_CH_11030').id
        account_ids |= cli.env.ref('scenario.pcg_CH_20410').id

        logging.info('Force reconcile with account.mass.reconcile')

        for account in account_ids:
            mass_reconcile = AccountMassReconcile.search(
                [('account', '=', account)])
            mass_reconcile.run_reconcile()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--env', choices=['dev', 'integration', 'prod'],
                        required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    fix_reconcile(config)
