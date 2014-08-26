# -*- coding: utf-8 -*-
from support import *
import logging
from support.tools import model

logger = logging.getLogger('openerp.behave')

@given('I set the taxes on all products')
def impl(ctx):

    def get_by_xmlid(xmlid):
        module, name = xmlid.split('.')
        search_domain = [('module', '=', module), ('name', '=', name)]
        record = model('ir.model.data').browse(search_domain)
        return record.res_id

    def get_tax(descr, company_id):
        domain = [('description', '=', descr),
                  ('company_id', '=', company_id)]
        return model('account.tax').get(domain)

    company_ch = get_by_xmlid('scenario.qoqa_ch')
    company_fr = get_by_xmlid('scenario.qoqa_fr')
    saletax_ch = get_tax('8.0%', company_ch)
    purchtax_ch = get_tax('8.0% achat', company_ch)
    saletax_fr = get_tax('19.6', company_fr)
    purchtax_fr = get_tax('ACH-19.6', company_fr)

    ProductProduct = model('product.product')
    ids = ProductProduct.search()
    values = {'taxes_id': [(6, 0, [saletax_ch.id, saletax_fr.id])],
              'supplier_taxes_id': [(6, 0, [purchtax_ch.id, purchtax_fr.id])],
              }
    ProductProduct.write(ids, values)

@given('I write the current standard price on products to update the stored function fields')
def impl(ctx):
    std_prices = model('product.price.history').browse(['name = standard_price'])
    templates = [stdp.product_id for stdp in std_prices]
    products = [variant for tmpl in templates for variant in tmpl.variant_ids]
    for product in products:
        product.write({'standard_price': product.standard_price})
