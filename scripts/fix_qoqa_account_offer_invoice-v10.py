# -*- coding: utf-8 -*-
import time
from random import randint
from Queue import Queue, Empty
from threading import Thread, Lock
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

WORKERS = 3


class SaveStateManger(object):

    def __init__(self):
        self.file_lock = Lock()
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
        if not len(self.processed_invoices) % 50:
            self.save()

    def save(self):
        self.file_lock.acquire()
        with open(SAVESTATE_PATH, 'wb') as save_state_file:
            cPickle.dump(self.processed_invoices, save_state_file)
        self.file_lock.release()


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


def unreconcile_from_invoice(odoo, invoice, save_manager, work_queue):
    inv_id = invoice.id
    if invoice.move_id:
        print "try to unreconcile invoice {}".format(invoice.number)
        try:
            move = invoice.move_id
            for move_line in move.line_ids:
                move_line.remove_move_reconcile()
            invoice.action_cancel()
            invoice.action_cancel_draft()

        except odoorpc.error.RPCError as exc:
            if exc.info.get('data', {}).get('name') == 'psycopg2.OperationalError':
                raise
            try:
                Invoice = odoo.env['account.invoice']
                # we force rebowse
                invoice = Invoice.browse(inv_id)
                for move in invoice.payment_move_line_ids:
                    move.remove_move_reconcile()
                invoice.action_cancel()
                invoice.action_cancel_draft()
            except odoorpc.error.RPCError as exc:
                raise


def move_lines_are_valid(odoo, invoice, save_manager):
    MoveLine = odoo.env['account.move.line']
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
                return False
    return True


def unreconcile_worker(save_manager, config, work_queue):
    odoo = rpc_client(config)
    Invoice = odoo.env['account.invoice']
    InvoiceLine = odoo.env['account.invoice.line']
    while "Ureconciling invoices":
        try:
            inv_id = work_queue.get_nowait()
        except Empty:
            print "worker stopped"
            return
        if inv_id in save_manager:
            print 'SKIPPED id {}'.format(inv_id)
            work_queue.task_done()
            continue

        time.sleep(randint(0, 5))
        invoice = Invoice.browse(inv_id)
        print "working on: invoice {} number {} on {}".format(inv_id, invoice.name, work_queue.qsize())
        if not move_lines_are_valid(odoo, invoice, save_manager):
            work_queue.task_done()
            continue
        # trick the invoice as computed field is not updated on time
        try:
            unreconcile_from_invoice(odoo, invoice, save_manager, work_queue)
            invoice = Invoice.browse(inv_id)
            invoice_line_ids = InvoiceLine.search(
            [('invoice_id', '=', inv_id)])
            invoice_lines = InvoiceLine.browse(invoice_line_ids)
            for invoice_line in invoice_lines:
                if invoice_line.product_id.taxes_id !=\
                        invoice_line.invoice_line_tax_ids:
                    print "REWRITE TAXES for invoice {}".format(
                        invoice.name)
                    tax_tab = [x.id for x in invoice_line.product_id.taxes_id]
                    invoice_line.sale_line_ids.write(
                        {'tax_id': [(6, 0, tax_tab)]})
                    invoice_line.write(
                        {'invoice_line_tax_ids': [(6, 0, tax_tab)]}
                    )
                    print "REWRITE TAXES for invoice {} done".format(
                        invoice.name)
            invoice.signal_workflow('invoice_open')
            save_manager.add(invoice.id)
            work_queue.task_done()
        except odoorpc.error.RPCError as exc:
            if exc.info.get('data', {}).get('name') == 'psycopg2.OperationalError':
                print "Cursor error for invoice {} back in queue".format(
                    invoice.name)
                work_queue.put(inv_id)
                work_queue.task_done()
                continue
            else:
                logging.info("Unexpected error - {} must be processed manually".format(invoice.name))
                save_manager.add(invoice.id)


def fix_invoice_offer(offer_list, save_manager, config=False):
    work_queue = Queue()
    logging.debug('---------START------------')
    odoo = rpc_client(config)
    # We reconpute all refund
    Invoice = odoo.env['account.invoice']
    QoqaOffer = odoo.env['qoqa.offer']
    offer_ids = QoqaOffer.search([('ref', 'in', offer_list)])
    invoice_ids = Invoice.search([('offer_id', 'in', offer_ids),
                                  ('company_id', '=', 3),
                                  ('type', '=', 'out_invoice'),
                                  ('state', 'in', ['open', 'paid'])])
    #  account_id
    #   id  | code
    # ------+-------
    #   576 | 32000
    #  2702 | 32001
    #  2706 | 32005
    for inv_id in invoice_ids:
        if inv_id in save_manager:
            print 'SKIPPED id {}'.format(inv_id)
        else:
            work_queue.put(inv_id)
    workers = []
    for _ in range(WORKERS):
        worker = Thread(target=unreconcile_worker,
                        args=(save_manager, config, work_queue))
        workers.append(worker)
        worker.setDaemon(True)
        worker.start()
    try:
        while True:
            if not work_queue.empty():
                time.sleep(1)
            else:
                break
    except KeyboardInterrupt:
        print "stopping threads"
        while "stopping threads":
            try:
                work_queue.get_nowait()
                work_queue.task_done()
            except Empty:
                break
        for w in workers:
            w.join()
        return

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
