#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import ConfigParser
import odoorpc
import psycopg2
import psycopg2.extras


SO_LIST = ['03399162',
           '03397044',
           '03334543',
           '03334553',
           '03333997',
           '03333521',
           '03332829',
           '03333068',
           '03332453',
           '03332389',
           '03331908',
           '03331717',
           '03331857',
           '03331478',
           '03325624',
           '03325466',
           '03325400',
           '03322952',
           '03322156',
           '03320449',
           '03319571',
           '03319276',
           '03318832',
           '03318477',
           '03317480',
           '03315757',
           '03314805',
           '03314856',
           '03314568',
           '03314034',
           '03313820',
           '03313648',
           '03313417',
           '02730536',
           '02730464',
           '02730153',
           '02729932',
           '02693355',
           '02690371',
           '02690231',
           '02611179',
           '02611163',
           '02611089',
           '02546222',
           '02545796',
           '02545673',
           '02545671',
           '02545639',
           '02544784',
           '02544548',
           '02544593',
           '02544564',
           '02450058',
           '02332965',
           '02332037',
           '02331837',
           '02330349',
           '02328316',
           '02330095',
           '02328207',
           '02235324',
           '02229969',
           '02229500',
           '02229322',
           '02229278',
           '02229154',
           '02227854',
           '02227718',
           '02227468',
           '02227209',
           '02227191',
           '02226910',
           '02201681',
           '02183404',
           '02169797',
           '02169713',
           '02169506',
           '02169472',
           '02169107',
           '02169102',
           '02168918',
           '02146560',
           '02146190',
           '02146038',
           '02145821',
           '02145714',
           '02145650',
           '02145454',
           '02145292',
           '02145225',
           '02145210',
           '02145031',
           '02140485',
           '02140509',
           '02140219',
           '02140229',
           '02140137',
           '02137623',
           '02139912',
           '02139739',
           '02139433',
           '02138634',
           '02137929',
           '02137846',
           '02137339',
           '02137334',
           '02137307',
           '02096554',
           '02096487',
           '02095502',
           '02095062',
           '02094961',
           '02094929',
           '02073157',
           '02022000',
           '02021997',
           '01983463',
           '01983244',
           '01982410',
           '01982389',
           '01982355',
           '01982291',
           '01970929',
           '01970462',
           '01970074',
           '01969747',
           '01969264',
           '01969020',
           '01921213',
           '01920867',
           '01920324',
           '01919173',
           '01918165',
           '01918359',
           '01918302',
           '01802154',
           '01791972',
           '01791641',
           '01718393',
           '01718231',
           '01718067',
           '01717842',
           '01717419',
           '01717137',
           '01717088',
           '01717008']


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

    cli = rpc_client(config)
    cli.login(config['db'], admin_ch, config['admin_ch'])
    cli.env.context['active_test'] = False

    SaleOrder = cli.env['sale.order']
    AccountMassReconcile = cli.env['account.mass.reconcile']

    # SO_LIST = name so to take care of
    sale_order_ids = SaleOrder.browse(
        SaleOrder.search([('name', 'in', SO_LIST)])
    )

    # Unreconcile account.move.line and set invoice back to open
    for sale_order in sale_order_ids:
        for invoice in sale_order.invoice_ids:
            if invoice.move_id:
                if invoice.move_id.line_ids:
                    for move_line in invoice.move_id.line_ids:
                        move_line.remove_move_reconcile()
            invoice.write({'state': 'open'})

    # Reconcile with mass reconcile
    account_ids = cli.env['account.account'].browse(
        [cli.env.ref('scenario.pcg_CH_11030').id,
         cli.env.ref('scenario.pcg_CH_20410').id]
    )
    for account in account_ids:
        mass_reconcile = AccountMassReconcile.browse(
            AccountMassReconcile.search([('account', '=', account.id)])
        )
        mass_reconcile.run_reconcile()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--env', choices=['dev', 'integration', 'prod'],
                        required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    fix_reconcile(config)
