# -*- coding: utf-8 -*-
import logging

from contextlib import closing, contextmanager
from support import *
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


@contextmanager
def newcr(ctx):
    openerp = ctx.conf['server']
    db_name = ctx.conf['db_name']

    registry = openerp.modules.registry.RegistryManager.new(db_name)
    with closing(registry.cursor()) as cr:
        try:
            yield cr
        except:
            cr.rollback()
            raise
        else:
            cr.commit()


@given('I migrate the product attribute variants')
def impl(ctx):
    with newcr(ctx) as cr:
        cr.execute("SELECT * FROM product_variant_dimension_type")
        for dimension_type in cr.dictfetchall():
            cr.execute(
                'SELECT id FROM product_attribute '
                'WHERE name = %s ',
                (dimension_type['name'],)
            )
            row = cr.fetchone()
            if row:
                attribute_id = row[0]
            else:
                cr.execute(
                    'INSERT INTO product_attribute '
                    '(name, create_date, write_date, create_uid, write_uid) '
                    'VALUES (%s, %s, %s, %s, %s) '
                    'RETURNING id',
                    (dimension_type['name'],
                     dimension_type['create_date'],
                     dimension_type['write_date'],
                     dimension_type['create_uid'],
                     dimension_type['write_uid'])
                )
                attribute_id = cr.fetchone()[0]
            cr.execute('SELECT * from product_variant_dimension_option '
                       'WHERE type_id = %s', (dimension_type['id'],))
            for option in cr.dictfetchall():
                    cr.execute(
                        'SELECT id FROM product_attribute_value '
                        'WHERE attribute_id = %s '
                        'AND name = %s ',
                        (attribute_id, option['name'])
                    )
                    if not cr.fetchone():
                        cr.execute(
                            'INSERT INTO product_attribute_value '
                            '(attribute_id, name, create_date, write_date, '
                            ' create_uid, write_uid) '
                            'VALUES (%s, %s, %s, %s, %s, %s) ',
                            (attribute_id,
                             option['name'],
                             option['create_date'],
                             option['write_date'],
                             option['create_uid'],
                             option['write_uid'])
                        )
