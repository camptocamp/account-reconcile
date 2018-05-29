# -*- coding: utf-8 -*-
# Copyright 2016-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os

from base64 import b64encode
from pkg_resources import Requirement, resource_string

import anthem

from anthem.lyrics.records import create_or_update
from ..common import create_default_value


@anthem.log
def setup_company(ctx, req):
    """ Setup company """
    company = ctx.env.ref('base.main_company')
    company.name = 'QoQa Holding'

    # load logo on company
    logo_content = resource_string(req, 'data/images/logo_qoqa_ch.png')
    b64_logo = b64encode(logo_content)
    company.logo = b64_logo

    with ctx.log(u'Configuring CH company'):
        connector_user_ch = ctx.env.ref('connector_qoqa.user_connector_ch')
        values = {
            'name': "QoQa Services SA",
            'street': "Rue de l'Arc-en-Ciel 14",
            'zip': "1030",
            'city': "Bussigny-Lausanne",
            'country_id': ctx.env.ref('base.ch').id,
            'phone': "+41 21 633 20 80",
            'fax': "+41 21 633 20 81",
            'email': "contact@qoqa.ch",
            'website': "http://www.qoqa.ch",
            'vat': "CHE-105.616.108 TVA",
            'parent_id': company.id,
            'qoqa_id': "1",
            'connector_user_id': connector_user_ch.id,
            'logo': b64_logo,
            'currency_id': ctx.env.ref('base.CHF').id,
        }
        create_or_update(ctx, 'res.company', 'scenario.qoqa_ch', values)

    with ctx.log(u'Configuring FR company'):
        fr_logo_content = resource_string(req, 'data/images/logo_qoqa_fr.png')
        connector_user_ch = ctx.env.ref('connector_qoqa.user_connector_fr')
        values = {
            'name': "QoQa Services France",
            'street': "20 rue Georges Barres",
            'zip': "33300",
            'city': "Bordeaux",
            'country_id': ctx.env.ref('base.fr').id,
            'phone': "+33 5 56 37 57 08",
            'fax': "+33 5 56 37 57 08",
            'email': "clients@qoqa.fr",
            'website': "http://www.qoqa.fr",
            'vat': "FR80 504 886 607",
            'company_registry': "504 886 607",
            'siret': "504 886 607 00036",
            'ape': "4791 A",
            'parent_id': company.id,
            'qoqa_id': "2",
            'connector_user_id': connector_user_ch.id,
            'logo': b64encode(fr_logo_content),
            'currency_id': ctx.env.ref('base.CHF').id,
        }
        create_or_update(ctx, 'res.company', 'scenario.qoqa_ch', values)


@anthem.log
def setup_language(ctx):
    """ Installing language and configuring locale formatting """
    for code in ('fr_FR', 'de_DE'):
        ctx.env['base.language.install'].create({'lang': code}).lang_install()
    ctx.env['res.lang'].search([]).write({
        'grouping': [3, 0],
        'date_format': '%d/%m/%Y',
    })


@anthem.log
def default_values(ctx):
    """ Defining some default values """
    for company in ctx.env['res.company'].search([]):
        create_default_value(ctx,
                             'product.template',
                             'purchase_method',
                             company.id,
                             'purchase')


@anthem.log
def create_sale_teams(ctx):
    """ Create sales team required in qoqa_claim_unclaimed_process

    """
    values = {
        'name': "Livraisons",
    }
    create_or_update(
        ctx, 'crm.team', 'scenario.section_sale_team_livr', values)


@anthem.log
def admin_user_password(ctx):
    """ Changing admin password """
    # Password is in lastpass:
    # [odoo-test] qoqa test admin user
    # In the lastpass directory: Shared-C2C-Odoo-External
    if os.environ.get('RUNNING_ENV') == 'dev':
        ctx.log_line('Not changing password for dev RUNNING_ENV')
        return
    ctx.env.user.password_crypt = (
        '$pbkdf2-sha512$12000$713rXct5730PQag1JmTs3Q$YqcgolwDaum.5jaqkltnE'
        '/Vv75r7C6cf7KfAufUeVqz4AwJePjqRQeb4IK8ciid91DpuwE0VMGlCFovKhv4I/w'
    )


@anthem.log
def main(ctx):
    """ Main: creating demo data """
    req = Requirement.parse('qoqa-odoo')
    setup_company(ctx, req)
    setup_language(ctx)
    default_values(ctx)
    create_sale_teams(ctx)
    admin_user_password(ctx)
    # TODO: generate demo data
