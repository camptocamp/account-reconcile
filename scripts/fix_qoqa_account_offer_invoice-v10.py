# -*- coding: utf-8 -*-
import os
import cPickle
import logging
import argparse
import ConfigParser
import odoorpc


FORMAT = '%(asctime)s --  %(message)s'
logging.basicConfig(filename='manual_invoice.log',
                    level=logging.INFO, format=FORMAT)

SAVESTATE_PATH = 'processed_invoice.pickle'


class SaveStateManger(object):

    def __init__(self):
        if os.path.exists(SAVESTATE_PATH):
            with open(SAVESTATE_PATH, 'rb') as save_state_file:
                processed_invoices = cPickle.load(save_state_file)
        self.processed_invoices = processed_invoices

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save()

    def __contains__(self, key):
        return key in self.processed_invoices

    def add(self, invoice_id):
        self.processed_invoices.append(invoice_id)

    def save(self):
        with open(SAVESTATE_PATH, 'wb') as save_state_file:
            cPickle.dump(self.processed_invoices, save_state_file)


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
    client.login(config['db'],
                 'admin_ch',
                 config['admin_ch'])
    return client


def unreconcile_from_invoice(invoice, save_manager):
    try:
        for move in invoice.payment_move_line_ids:
            move.remove_move_reconcile()
        invoice.action_cancel()
        invoice.action_cancel_draft()
    except:
        logging.info("Can not unreconcile - {} must be processed manually".format(invoice.number))
    finally:
        save_manager.add(invoice.id)


def run_mass_reconcile(odoo, accounts):

    AccountMassReconcile = odoo.env['account.mass.reconcile']
    for account in accounts:
        mass_reconcile = AccountMassReconcile.browse(
            AccountMassReconcile.search([('account', '=', account.id)])
        )
        mass_reconcile.run_reconcile()


def fix_invoice_offer(offer_list, save_manager, config=False):
    logging.debug('---------START------------')
    odoo = rpc_client(config)
    # We reconpute all refund
    Invoice = odoo.env['account.invoice']
    QoqaOffer = odoo.env['qoqa.offer']
    InvoiceLine = odoo.env['account.invoice.line']
    MoveLine = odoo.env['account.move.line']
    offer_ids = QoqaOffer.search([('ref', 'in', offer_list)])
    invoice_ids = Invoice.search([('offer_id', 'in', offer_ids),
                                  ('company_id', '=', 3),
                                  ('type', '=', 'out_invoice'),
                                  ('state', 'in', ['open', 'paid'])])
    cpt = 1
    len_invoices = len(invoice_ids)
    #  account_id
    #   id  | code
    # ------+-------
    #   576 | 32000
    #  2702 | 32001
    #  2706 | 32005
    for inv_id in invoice_ids:
        if inv_id in save_manager:
            print 'SKIPPED id {}'.format(inv_id)
            cpt += 1
            continue
        invoice = Invoice.browse(inv_id)
        print str("%s on %s: number %s" % (cpt, len_invoices, invoice.name))
        invoice_line_ids = InvoiceLine.search(
            [('invoice_id', '=', inv_id)])
        invoice_lines = InvoiceLine.browse(invoice_line_ids)
        full_reconcile = []
        partial_reconcile = []
        partial_reconcile2 = []
        if invoice.move_id:
            move = invoice.move_id
            for move_line in move.line_ids:
                if move_line.full_reconcile_id:
                    full_reconcile += MoveLine.search(
                        [('full_reconcile_id', '=',
                          move_line.full_reconcile_id.id),
                         ('id', '!=', move_line.id)])
                    # Check if full reconcilation is on the same
                partial_reconcile += move_line.matched_credit_ids.\
                    credit_move_id.ids
                partial_reconcile2 += move_line.matched_debit_ids.\
                    debit_move_id.ids
                all_account = [x.account_id.id for
                               x in MoveLine.browse(full_reconcile +
                                                    partial_reconcile +
                                                    partial_reconcile2)]
                if len(list(set(all_account))) > 1:
                    # If we have different account on move
                    # it's an error so skip this reconcile

                    logging.info(
                        "Different accounts - Invoice {} must be processed manually".format(invoice.number)
                    )
                    save_manager.add(invoice.id)
                    continue
                else:
                    move_line.remove_move_reconcile()
        # trick the invoice as computed field is not updated on time
        try:
            invoice.action_cancel()
            invoice.action_cancel_draft()
        except Exception:
            unreconcile_from_invoice(invoice, save_manager)
            continue

        for invoice_line in invoice_lines:
            if invoice_line.product_id.taxes_id !=\
                    invoice_line.invoice_line_tax_ids:
                print str("REWRITE TAXES")
                tax_tab = [x.id for x in invoice_line.product_id.taxes_id]
                invoice_line.sale_line_ids.write(
                    {'tax_id': [(6, 0, tax_tab)]})
                invoice_line.write({'invoice_line_tax_ids': [(6, 0, tax_tab)]})

        invoice.signal_workflow('invoice_open')
        save_manager.add(invoice.id)
        cpt += 1
        if not cpt % 1:
            save_manager.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--env',
                        choices=['dev', 'integration', 'prod'], required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    with SaveStateManger() as save_manager:
        config = get_config(args.config, args.env)
        fix_invoice_offer(
            ['12952',
             '12989',
             '13006',
             '13110',
             '13111',
             '13133',
             '13139',
             '13623',
             '13639',
             '13640',
             '13653',
             '13780',
             '13784',
             '13787',
             '13815',
             '13822',
             '13837',
             '13838',
             '13862',
             '13886',
             '13888',
             '13890',
             '13913',
             '13930',
             '13951',
             '13958',
             '13974',
             '13990',
             '13992',
             '13994',
             '14031',
             '14035',
             '14036',
             '13201',
             '13220'],
            save_manager,
            config=config)
