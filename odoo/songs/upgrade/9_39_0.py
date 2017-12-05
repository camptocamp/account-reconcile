# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import anthem
import datetime


@anthem.log
def create_vat_2018_fiscal_position(ctx):
    """ Create fiscal position and fiscal position rule for swiss VAT change
        on Jan 1st 2018"""

    qoqa_ch = ctx.env.ref('scenario.qoqa_ch')

    tax_sale_8_incl = ctx.env['account.tax'].search([
        ('amount', '=', 8.0), ('type_tax_use', '=', 'sale'),
        ('price_include', '=', True)])
    tax_sale_8_excl = ctx.env['account.tax'].search([
        ('amount', '=', 8.0), ('type_tax_use', '=', 'sale'),
        ('price_include', '=', False)])

    tax_sale_7_7_incl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 7.7), ('type_tax_use', '=', 'sale'),
            ('price_include', '=', True)])
    tax_sale_7_7_excl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 7.7), ('type_tax_use', '=', 'sale'),
            ('price_include', '=', False)])

    tax_purchase_8_incl = ctx.env['account.tax'].search([
        ('amount', '=', 8.0), ('type_tax_use', '=', 'purchase'),
        ('price_include', '=', True), ('description', 'like', '%achat%')])
    tax_purchase_8_excl = ctx.env['account.tax'].search([
        ('amount', '=', 8.0), ('type_tax_use', '=', 'purchase'),
        ('price_include', '=', False), ('description', 'like', '%achat%')])

    tax_purchase_7_7_incl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 7.7), ('type_tax_use', '=', 'purchase'),
            ('price_include', '=', True), ('description', 'like', '%achat%')])
    tax_purchase_7_7_excl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 7.7), ('type_tax_use', '=', 'purchase'),
            ('price_include', '=', False), ('description', 'like', '%achat%')])

    tax_invest_8_incl = ctx.env['account.tax'].search([
        ('amount', '=', 8.0), ('type_tax_use', '=', 'purchase'),
        ('price_include', '=', True), ('description', 'like', '%invest%')])
    tax_invest_8_excl = ctx.env['account.tax'].search([
        ('amount', '=', 8.0), ('type_tax_use', '=', 'purchase'),
        ('price_include', '=', False), ('description', 'like', '%invest%')])

    tax_invest_7_7_incl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 7.7), ('type_tax_use', '=', 'purchase'),
            ('price_include', '=', True), ('description', 'like', '%invest%')])
    tax_invest_7_7_excl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 7.7), ('type_tax_use', '=', 'purchase'),
            ('price_include', '=', False),
            ('description', 'like', '%invest%')])

    tax_sale_3_8_incl = ctx.env['account.tax'].search([
        ('amount', '=', 3.8), ('type_tax_use', '=', 'sale'),
        ('price_include', '=', True)])
    tax_sale_3_7_incl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 3.7), ('type_tax_use', '=', 'sale'),
            ('price_include', '=', True)])

    tax_invest_3_8_excl = ctx.env['account.tax'].search([
        ('amount', '=', 3.8), ('type_tax_use', '=', 'purchase'),
        ('price_include', '=', False), ('description', 'like', '%invest%')])
    tax_invest_3_7_excl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 3.7), ('type_tax_use', '=', 'purchase'),
            ('price_include', '=', False),
            ('description', 'like', '%invest%')])

    tax_invest_3_8_incl = ctx.env['account.tax'].search([
        ('amount', '=', 3.8), ('type_tax_use', '=', 'purchase'),
        ('price_include', '=', True), ('description', 'like', '%invest%')])
    tax_invest_3_7_incl = ctx.env['account.tax'].with_context(
        active_test=False).search([
            ('amount', '=', 3.7), ('type_tax_use', '=', 'purchase'),
            ('price_include', '=', True),
            ('description', 'like', '%invest%')])

    inactive_taxes = (tax_sale_7_7_incl | tax_sale_7_7_excl |
                      tax_purchase_7_7_incl | tax_purchase_7_7_excl |
                      tax_sale_3_7_incl | tax_invest_3_7_excl |
                      tax_invest_3_7_incl)
    inactive_taxes.write({'active': True})

    fiscal_position_2018 = ctx.env['account.fiscal.position'].create({
        'name': 'Swiss TVA 2018',
        'company_id': qoqa_ch.id,
        'tax_ids': [(0, 0, {
            'tax_src_id': tax_sale_8_incl.id,
            'tax_dest_id': tax_sale_7_7_incl.id,
        }), (0, 0, {
            'tax_src_id': tax_sale_8_excl.id,
            'tax_dest_id': tax_sale_7_7_excl.id,
        }), (0, 0, {
            'tax_src_id': tax_purchase_8_incl.id,
            'tax_dest_id': tax_purchase_7_7_incl.id,
        }), (0, 0, {
            'tax_src_id': tax_purchase_8_excl.id,
            'tax_dest_id': tax_purchase_7_7_excl.id,
        }), (0, 0, {
            'tax_src_id': tax_invest_8_incl.id,
            'tax_dest_id': tax_invest_7_7_incl.id,
        }), (0, 0, {
            'tax_src_id': tax_invest_8_excl.id,
            'tax_dest_id': tax_invest_7_7_excl.id,
        }), (0, 0, {
            'tax_src_id': tax_sale_3_8_incl.id,
            'tax_dest_id': tax_sale_3_7_incl.id,
        }), (0, 0, {
            'tax_src_id': tax_invest_3_8_excl.id,
            'tax_dest_id': tax_invest_3_7_excl.id,
        }), (0, 0, {
            'tax_src_id': tax_invest_3_8_incl.id,
            'tax_dest_id': tax_invest_3_7_incl.id,
        })]
    })

    ctx.env['account.fiscal.position.rule'].create({
        'name': 'Swiss TVA 2018',
        'description': 'Changement de TVA en Suisse au 01.01.2018',
        'company_id': qoqa_ch.id,
        'fiscal_position_id': fiscal_position_2018.id,
        'date_start': datetime.date(2018, 01, 01),
        'use_sale': True,
        'use_purchase': True,
        'use_invoice': True,
    })


@anthem.log
def main(ctx):
    """ Applying update 9.39.0"""
    create_vat_2018_fiscal_position(ctx)
