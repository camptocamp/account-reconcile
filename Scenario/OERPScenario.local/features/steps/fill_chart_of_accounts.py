from support import *
import datetime
import csv
import os.path as osp
import pprint
import bisect
import logging

import erppeek

logger = logging.getLogger('openerp.behave')

DATADIR = osp.abspath(osp.join(osp.dirname(__file__), '..', '..', 'data'))
class csv_dialect_chart:
    delimiter = ';'
    quotechar = '"'
    escapechar = None
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = csv.QUOTE_MINIMAL

@step('Create external ids for accounts from "{filename}"')
def impl(ctx, filename):
    AccountAccount = model('account.account')
    IrModelData = model('ir.model.data')
    company_id = getattr(ctx, 'company_id', False)

    filename = osp.join(DATADIR, filename)
    with open(filename) as fobj:
        reader = csv.DictReader(fobj, dialect=csv_dialect_chart)
        for row in reader:
            code = row['code']
            if '.' in row['id']:
                module, external_id = row['id'].split('.')
            else:
                module = ''
                external_id = row['id']
            account_list = AccountAccount.browse([('company_id', '=', company_id),
                                             ('code', '=', code)])
            # if an account with this code exists
            if account_list:
                account = account_list[0]
                xml_ref = IrModelData.browse([('model', '=', 'account.account'),
                                              ('res_id', '=', account.id),
                                              ('name', '=', external_id),
                                              ('module', '=', module)])
                if not xml_ref:
                    data = {'model': 'account.account',
                            'res_id': account.id,
                            'name': external_id,
                            'module': module,
                            }
                    IrModelData.create(data)


@step('I fill the chart using "{filename}"')
def impl(ctx, filename):
    AccountAccount = model('account.account')
    company_id = getattr(ctx, 'company_id', False)
    account_ids = dict((account.code.encode('cp1252'), (account.id, account.user_type))
                         for account in AccountAccount.browse([('company_id', '=', company_id),
                                                               ('type', '=', 'view')]))

    account_codes = sorted(account_ids)
    assert account_codes, "No accounts found for company_id %s" % company_id
    new_accounts = []
    filename = osp.join(DATADIR, filename)
    with open(filename) as fobj:
        reader = csv.DictReader(fobj, ['code', 'name'], dialect=csv_dialect_chart)
        for row in reader:
            if row['code'].startswith('0'):
                continue
            idx = bisect.bisect_right(account_codes, row['code'])
            parent_code = account_codes[idx-1]
            parent_id, parent_user_type = account_ids[parent_code]
            #logger.info('parent of %s is %s', row['code'], parent_code)
            new_accounts.append((row['code'], row['name'].decode('cp1252'), parent_code, parent_id, parent_user_type))

    user_types = {}
    for q_account, q_name, parent_code, parent_id, parent_user_type in new_accounts:
        q_name = q_name.capitalize()
        if parent_code.ljust(8, '0') == q_account:
            continue
        account = AccountAccount.browse([('company_id', '=', company_id),
                                                   ('code', '=', q_account)])
        if account:
            if account[0].name != q_name:
                logger.info('renaming account %s from %r to %r', q_account, account[0].name, q_name)
                account[0].name = q_name
            continue
        if q_account == u'41110000':
            internal_type = 'payable'
        elif q_account == '40110000':
            internal_type = 'receivable'
        else:
            internal_type = 'other'
        if parent_id not in user_types:
            types = AccountAccount.browse([('company_id', '=', company_id),
                                           ('parent_id', '=', parent_id)],
                                          limit=1)
            if types:
                user_type_id = types[0].user_type.id
            else:
                user_type_id = None
            user_types[parent_id] = user_type_id
        else:
            user_type_id = user_types[parent_id]
        if user_type_id is None:
            logger.warning('cannot create account %s: no user_type', q_account)
            continue
        values = {'name': q_name,
                  'code': q_account,
                  'type': internal_type,
                  'user_type': user_type_id,
                  'parent_id': parent_id,
                  'company_id': company_id,
                  'active': True,
                  }
        logger.info('create account %s', values)
        AccountAccount.create(values, context={'defer_parent_store_computation': True})
    recompute_parents_impl(ctx)

@step('I recompute parents of account.account')
def recompute_parents_impl(ctx):
    registry = erppeek.get_pool(ctx.conf['db_name'])
    registry._init_parent['account.account'] = True
    cursor = registry.db.cursor()
    registry.do_parent_store(cursor)
    cursor.commit()
    cursor.close()


@step('I remove tax_ids on account.account')
def impl(ctx):
    company_id = getattr(ctx, 'company_id', False)
    account_ids = model('account.account').search([('company_id', '=', company_id)])
    model('account.account').write(account_ids,
                                   {'tax_ids': [(5,)],
                                    })
