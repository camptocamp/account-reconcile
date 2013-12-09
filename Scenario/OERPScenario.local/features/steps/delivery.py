# -*- coding: utf-8 -*-
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')

@given(u'I update postlogistics services')
def impl(ctx):
    """
    Update postlogistics services to create or update
    delivery carrier options by calling the settings transient model
    """
    cp_id = getattr(ctx, 'company_id')
    company = model('res.company').get([('id', '=', cp_id)])
    assert company

    configuration_wizard = model('postlogistics.config.settings').create({'company_id': company.id})

    vals = configuration_wizard.onchange_company_id(company.id)
    configuration_wizard.write(vals['value'])
    configuration_wizard.update_postlogistics_options()
