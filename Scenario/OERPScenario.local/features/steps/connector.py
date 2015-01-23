# -*- coding: utf-8 -*-

import csv
import logging

from support import *
from support.tools import model

logger = logging.getLogger('openerp.behave')


def _fileopen(ctx, filename, mode='r'):
    tmp_path = ctx.feature.filename.split(os.path.sep)
    tmp_path = tmp_path[1: tmp_path.index('features')] + ['data', '%s'%filename]
    tmp_path = [str(x) for x in tmp_path]
    path = os.path.join('/', *tmp_path)
    assert os.path.exists(path)
    return open(path, mode)


@step('I import from QoQa the "{import_model}" with QoQa ids from file "{path}"')
def impl(ctx, import_model, path):
    """
    Import records from QoQa using the connector
    """
    data = csv.reader(_fileopen(ctx, path))
    qoqa_ids = (row[0] for row in data)
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']

    connector_qoqa = openerp.addons.connector_qoqa
    import_record = connector_qoqa.unit.import_synchronizer.import_record
    ConnectorSessionHandler = openerp.addons.connector.session.ConnectorSessionHandler
    session_hdl = ConnectorSessionHandler(db_name, 1)
    with session_hdl.session() as session:
        for qoqa_id in qoqa_ids:
            import_record.delay(session, import_model,
                                1, qoqa_id, force=True)


@step('I import again from QoQa the offer position with a missing lot price')
def impl(ctx):
    """
    Import records from QoQa using the connector
    """
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']

    Position = model('qoqa.offer.position')
    positions = Position.browse(['lot_price = 0', 'qoqa_id != False'])

    connector_qoqa = openerp.addons.connector_qoqa
    import_record = connector_qoqa.unit.import_synchronizer.import_record
    ConnectorSessionHandler = openerp.addons.connector.session.ConnectorSessionHandler
    session_hdl = ConnectorSessionHandler(db_name, 1)
    with session_hdl.session() as session:
        for position in positions:
            import_record.delay(session, 'qoqa.offer.position',
                                1, position.qoqa_id, force=True)


@step('I re-import from QoQa the promo issuances with unbalanced lines')
def impl(ctx):
    """
    Import records from QoQa using the connector
    """
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']

    Issuance = model('qoqa.promo.issuance.line')
    Move = model('account.move')

    promo_issuances = Issuance.browse([('state', '=', 'draft'),
                                       ('qoqa_issuance_id', '!=', False)])
    issuances = [x.qoqa_issuance_id for x in promo_issuances]
    qoqa_ids = list(set([x.qoqa_id for x in issuances]))
    move_ids = list(set([x.openerp_id.id for x in issuances]))
    Move.unlink(move_ids)
    print "%s moves deleted" % (len(move_ids))

    connector_qoqa = openerp.addons.connector_qoqa
    import_accounting_issuance = connector_qoqa.accounting_issuance.importer.import_accounting_issuance
    ConnectorSessionHandler = openerp.addons.connector.session.ConnectorSessionHandler
    session_hdl = ConnectorSessionHandler(db_name, 1)
    with session_hdl.session() as session:
        for qoqa_id in qoqa_ids:
            import_accounting_issuance.delay(session,
                                             'qoqa.accounting.issuance',
                                             1, int(qoqa_id), force=False)
