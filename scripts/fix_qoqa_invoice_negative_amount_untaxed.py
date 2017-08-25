# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import odoorpc
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


def fix_negative_amount_untaxed_invoices(invoice_ids=[], config=False):
    odoo = rpc_client(config)
    # We reconpute all refund
    Invoice = odoo.env['account.invoice']
    cpt = 1
    len_invoices = len(invoice_ids)
    for inv_id in invoice_ids:
        invoice = Invoice.browse(inv_id)
        print str("%s on %s: number %s" % (cpt, len_invoices, invoice.name))
        if invoice.move_id:
            move = invoice.move_id
            for move_line in move.line_ids:
                move_line.remove_move_reconcile()
        # trick the invoice as computed field is not updated on time
        invoice.write({'refund_description_id': 27})
        invoice.action_cancel()
        cpt += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--env',
                        choices=['dev', 'integration', 'prod'], required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    fix_negative_amount_untaxed_invoices(
        invoice_ids=[
            2715760,
            2724579,
            2758907,
            2776055,
            2780686,
            2796998,
            2803389,
            2809223
        ],
        config=config)
