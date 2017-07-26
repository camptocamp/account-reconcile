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


def fix_invoice_offer(offer_list=[], config=False):
    odoo = rpc_client(config)
    # We reconpute all refund
    Invoice = odoo.env['account.invoice']
    QoqaOffer = odoo.env['qoqa.offer']
    InvoiceLine = odoo.env['account.invoice.line']
    MoveLine = odoo.env['account.move.line']
    offer_ids = QoqaOffer.search([('ref', 'in', offer_list)])
    invoice_ids = Invoice.search([('offer_id', 'in', offer_ids),
                                  ('company_id', '=', 3),
                                  ('type', '=', 'out_invoice')])
    cpt = 1
    len_invoices = len(invoice_ids)
    #  account_id
    #   id  | code
    # ------+-------
    #   576 | 32000
    #  2702 | 32001
    #  2706 | 32005
    for inv_id in invoice_ids:
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
                partial_reconcile = move_line.matched_credit_ids.ids
                partial_reconcile2 = move_line.matched_debit_ids.ids
                # We will now inreconcile all-lines.
                move_line.remove_move_reconcile()
        # trick the invoice as computed field is not updated on time
        invoice.action_cancel()
        invoice.action_cancel_draft()
        for invoice_line in invoice_lines:
            if invoice_line.product_id.taxes_id !=\
                    invoice_line.invoice_line_tax_ids:
                print str("REWRITE TAXES")
                tax_tab = [x.id for x in invoice_line.product_id.taxes_id]
                invoice_line.sale_line_ids.write(
                    {'tax_id': [(6, 0, tax_tab)]})
                invoice_line.write({'invoice_line_tax_ids': [(6, 0, tax_tab)]})

        invoice.signal_workflow('invoice_open')
        print ("Full: %s Credit Match: %s DEBIT MATCH: %s"
               % (full_reconcile,
                  partial_reconcile,
                  partial_reconcile2))
        if full_reconcile or partial_reconcile or partial_reconcile2:
            # XXX get updated invoice as move has changed ??
            invoice = Invoice.browse(invoice.id)
            move_line_ids = MoveLine.search(
                [('move_id', '=', invoice.move_id.id),
                 ('account_id', '=', invoice.account_id.id)])

            to_reconcile_ids = move_line_ids + full_reconcile + \
                partial_reconcile + partial_reconcile2
            move_lines = MoveLine.browse(to_reconcile_ids)
            move_lines.reconcile()
        cpt += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--env',
                        choices=['dev', 'integration', 'prod'], required=True)
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()
    config = get_config(args.config, args.env)
    fix_invoice_offer(
        offer_list=[
            '12952',
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
        config=config)
