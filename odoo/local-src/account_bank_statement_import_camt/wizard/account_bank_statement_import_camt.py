# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# flake8: noqa
# (since it is Odoo's code backported, it won't be PEP8)

from lxml import etree
from StringIO import StringIO

from openerp import models
from openerp.addons.account_bank_statement_import.account_bank_statement_import \
    import sanitize_account_number as old_sanitize


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    def _complete_stmts_vals(self, stmts_vals, journal, account_number):
        # Ugly inherit to simply remove all the part about the bank account ;
        # otherwise, the parsed partners are lost
        for st_vals in stmts_vals:
            st_vals['journal_id'] = journal.id

            for line_vals in st_vals['transactions']:
                unique_import_id = line_vals.get('unique_import_id')
                if unique_import_id:
                    sanitized_account_number = old_sanitize(account_number)
                    line_vals['unique_import_id'] = (sanitized_account_number and sanitized_account_number + '-' or '') + str(journal.id) + '-' + unique_import_id

        return stmts_vals

    def _check_camt(self, data_file):
        try:
            root = etree.parse(StringIO(data_file)).getroot()
        except:
            return False
        if root.tag.find('camt.053'):
            return root
        return False

    def _parse_file(self, data_file):
        root = self._check_camt(data_file)
        if root:
            return self._parse_file_camt(root)
        return super(AccountBankStatementImport, self)._parse_file(data_file)

    def _parse_file_camt(self, root):

        def find_partner_and_name(entry_text):
            camt = self.env['account.bank.statement.camt'].search([
                ('name', 'ilike', entry_text),
            ], limit=1)
            if camt:
                return (camt.partner_id.id, camt.memo_text)
            return (False, entry_text)

        ns = {k or 'ns': v for k, v in root.nsmap.iteritems()}
        statement_list = []
        for statement in root[0].findall('ns:Stmt', ns):
            statement_vals = {}
            statement_vals['name'] = statement.xpath('ns:Id/text()', namespaces=ns)[0]

            # Transaction Entries 0..n
            transactions = []
            sequence = 0
            for entry in statement.findall('ns:Ntry', ns):
                sequence += 1
                entry_vals = {
                    'sequence': sequence,
                }

                # Amount 1..1
                amount = float(entry.xpath('ns:Amt/text()', namespaces=ns)[0])

                # Credit Or Debit Indicator 1..1
                sign = entry.xpath('ns:CdtDbtInd/text()', namespaces=ns)[0]
                counter_party = 'Dbtr'
                if sign == 'DBIT':
                    amount *= -1
                    counter_party = 'Cdtr'
                entry_vals['amount'] = amount

                # Date 0..1
                transaction_date = entry.xpath('ns:ValDt/ns:Dt/text() | ns:BookgDt/ns:Dt/text()', namespaces=ns)
                entry_vals['date'] = transaction_date and transaction_date[0] or False

                # Name 0..1
                transaction_name = entry.xpath('.//ns:AddtlNtryInf/text()', namespaces=ns)
                if transaction_name:
                    entry_vals['partner_id'], entry_vals['name'] = find_partner_and_name(transaction_name[0])
                # Bank Account No
                bank_account_no = entry.xpath(""".//ns:RltdPties/ns:%sAcct/ns:Id/ns:IBAN/text() |
                                                  (.//ns:%sAcct/ns:Id/ns:Othr/ns:Id)[1]/text()
                                                  """ % (counter_party, counter_party), namespaces=ns)
                entry_vals['account_number'] = bank_account_no and bank_account_no[0] or False

                # Reference 0..1
                # Structured communication if available
                ref = entry.xpath('.//ns:RmtInf/ns:Strd/ns:%sRefInf/ns:Ref/text()' % (counter_party,), namespaces=ns)
                if not ref:
                    # Otherwise, any of below given as reference
                    ref = entry.xpath("""ns:AcctSvcrRef/text() | ns:NtryDtls/ns:TxDtls/ns:Refs/ns:TxId/text() |
                                      ns:NtryDtls/ns:TxDtls/ns:Refs/ns:InstrId/text() | ns:NtryDtls/ns:TxDtls/ns:Refs/ns:EndToEndId/text() |
                                      ns:NtryDtls/ns:TxDtls/ns:Refs/ns:MndtId/text() | ns:NtryDtls/ns:TxDtls/ns:Refs/ns:ChqNb/text()
                                      """, namespaces=ns)
                entry_vals['ref'] = ref and ref[0] or False
                unique_import_ref = entry.xpath('ns:AcctSvcrRef/text()', namespaces=ns)
                entry_vals['unique_import_id'] = unique_import_ref and unique_import_ref[0] or statement_vals['name'] + '-' + str(sequence)

                transactions.append(entry_vals)
            statement_vals['transactions'] = transactions

            # Start Balance
            # any (OPBD, PRCD, ITBD):
            #   OPBD : Opening Balance
            #   PRCD : Previous Closing Balance
            #   ITBD : Interim Balance (in the case of preceeding pagination)
            start_amount = float(statement.xpath("ns:Bal/ns:Tp/ns:CdOrPrtry[ns:Cd='OPBD' or ns:Cd='PRCD' or ns:Cd='ITBD']/../../ns:Amt/text()",
                                                              namespaces=ns)[0])
            # Credit Or Debit Indicator 1..1
            sign = statement.xpath('ns:Bal/ns:CdtDbtInd/text()', namespaces=ns)[0]
            if sign == 'DBIT':
                start_amount *= -1
            statement_vals['balance_start'] = start_amount
            # Ending Balance
            # Statement Date
            # any 'CLBD', 'CLAV'
            #   CLBD : Closing Balance
            #   CLAV : Closing Available
            end_amount = float(statement.xpath("ns:Bal/ns:Tp/ns:CdOrPrtry[ns:Cd='CLBD' or ns:Cd='CLAV']/../../ns:Amt/text()",
                                                              namespaces=ns)[0])
            sign = statement.xpath('ns:Bal/ns:CdtDbtInd/text()', namespaces=ns)[0]
            if sign == 'DBIT':
                end_amount *= -1
            statement_vals['balance_end_real'] = end_amount

            statement_vals['date'] = statement.xpath("ns:Bal/ns:Tp/ns:CdOrPrtry[ns:Cd='CLBD' or ns:Cd='CLAV']/../../ns:Dt/ns:Dt/text()",
                                                              namespaces=ns)[0]
            statement_list.append(statement_vals)

            # Account Number    1..1
            # if not IBAN value then... <Othr><Id> would have.
            account_no = statement.xpath('ns:Acct/ns:Id/ns:IBAN/text() | ns:Acct/ns:Id/ns:Othr/ns:Id/text()', namespaces=ns)[0]
            # Currency 0..1
            currency = statement.xpath('ns:Acct/ns:Ccy/text() | ns:Bal/ns:Amt/@Ccy', namespaces=ns)[0]

        return currency, account_no, statement_list
