
@given(u'I need to validate all moves from "{date_from}" to "{date_to}" on company "{company_name}"')
def step_impl(ctx,date_from,date_to,company_name):
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']
    if openerp.release.version_info < (8,):
        pool = openerp.modules.registry.RegistryManager.get(db_name)
        cr = pool.db.cursor()
    else:
        registry = openerp.modules.registry.RegistryManager.new(db_name)
        cr = registry.cursor()
    # Get active Cron
    cron_model = model('ir.cron')
    active_con = cron_model.browse([('active', '=', True)]).id
    print str(active_con)
    cron_model.write(active_con,{'active':False})
    res_company_model = model('res.company')
    cp_id = res_company_model.browse([('name','=',company_name)])[0].id
    account_move_model = model('account.move')
    account_invoice_model = model('account.invoice')
    obj_sequence = model('ir.sequence')
    all_slash_move = account_move_model.browse([('name','=','/'),
                                                ('company_id','=',cp_id),
                                                ('date','>=',date_from),
                                                ('date','<=',date_to)])
    tot = len(all_slash_move)
    cpt = 1
    for slash_move in all_slash_move:
        # Search if an invoice is related, if yes do nothing we will wait
        new_name = False
        journal = slash_move.journal_id
        invoice = account_invoice_model.browse([('move_id','=',slash_move.id)])
        if invoice and invoice[0].internal_number:
            new_name = invoice[0].internal_number
        else:
            if journal.sequence_id:
                ctx_new = {'fiscalyear_id': slash_move.period_id.fiscalyear_id.id}
                new_name = obj_sequence.next_by_id(journal.sequence_id.id,ctx_new)
        if new_name:
            print '%s - %s' % (cpt, tot)
            sql = 'UPDATE account_move set name=\'%s\' where id = %s;' % (new_name, slash_move.id)
            cr.autocommit(True)
            cr.execute(sql)
            cpt += 1
    # Now we will post all move
    sql = 'UPDATE account_move set state=\'%s\' where date between \'%s\' and \'%s\';' % ('posted', date_from, date_to)
    try:
        cr.autocommit(True)
        cr.execute(sql)
        puts(cr.statusmessage)
    finally:
        cr.close()
    cron_model.write(active_con,{'active':True})
