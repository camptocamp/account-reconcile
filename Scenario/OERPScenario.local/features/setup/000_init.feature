# -*- coding: utf-8 -*-
###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@setup

Feature: Parameter the new database
  In order to have a coherent installation
  I've automated the manual steps.

  @createdb
  Scenario: CREATE DATABASE
    Given I create database from config file

  @webkit_path
  Scenario: SETUP WEBKIT path before running YAML tests
    Given I need a "res.company" with oid: base.main_company
    And I set the webkit path to "/srv/openerp/webkit_library/wkhtmltopdf-amd64"

  @modules
  Scenario: install modules
    Given I install the required modules with dependencies:
        | name                                            |
        # Base
        | account                                         |
        | multi_company                                   |
        | base_import                                     |
        | stock                                           |
        | sale                                            |
        # Base financial modules
        | account_constraints                             |
        | account_default_draft_move                      |
        | account_financial_report_webkit                 |
        | account_export_csv                              |
        | account_reversal                                |
        | currency_rate_update                            |
        | invoice_webkit                                  |
        # Banking framework
        | account_statement_base_completion               |
        | account_statement_base_import                   |
        | account_statement_commission                    |
        | account_statement_ext                           |
        | account_advanced_reconcile                      |
        | invoicing_voucher_killer                        |
        | statement_voucher_killer                        |
        # Banking reconcile with Transaction id
        | base_transaction_id                             |
        | account_statement_transactionid_completion      |
        | account_statement_transactionid_import          |
        # Margin
        | product_get_cost_field                          |
        | product_cost_incl_bom                           |
        | product_standard_margin                         |
        | product_historical_margin                       |
        | qoqa_offer_historical_margin                    |
        # Shipping labels
        | base_delivery_carrier_label                     |
        | delivery_carrier_label_postlogistics            |
        | delivery_carrier_label_postlogistics_shop_label |
        # Swiss localization
        | l10n_ch                                         |
        | l10n_ch_bank                                    |
        | l10n_ch_base_bank                               |
        | l10n_ch_dta                                     |
        | l10n_ch_payment_slip                            |
        | l10n_ch_zip                                     |
        | l10n_multilang                                  |
        # French localization
        | l10n_fr                                         |
        | l10n_fr_rib                                     |
        # ServerEnv and Mail, it pulls server_env and _files modules
        | mail_environment                                |
        # Other
        | sale_order_webkit                               |
        | connector_ecommerce                             |
        | connector_qoqa                                  |
        | purchase_landed_costs                           |
        | product_price_history                           |
        | crm_claim_rma                                   |
        | crm_rma_by_shop                                 |
        | specific_fct                                    |
        | specific_report                                 |
        | product_custom_attributes                       |
        | wine_ch_report                                  |
        | discount_coupon                                 |
        | qoqa_claim                                      |
        | qoqa_base_data                                  |
    Then my modules should have been installed and models reloaded

  @ged_setting
  Scenario: setup of GED
    Given I need a "ir.config_parameter" with key: ir_attachment.location
    And having:
      | key   | value                  |
      | key   | ir_attachment.location |
      | value | file:///filestore      |

  @lang
  Scenario: install lang
   Given I install the following language :
      | lang  |
      | fr_FR |
      | de_DE |
   Then the language should be available
    Given I find a "res.lang" with code: en_US
    And having:
         | key      | value  |
         | grouping | [3, 0] |
    Given I find a "res.lang" with code: fr_FR
    And having:
         | key      | value  |
         | grouping | [3, 0] |
    Given I find a "res.lang" with code: de_DE
    And having:
         | key      | value  |
         | grouping | [3, 0] |


  @currencies
  Scenario: Deactivate useless currencies
    Given  I execute the SQL commands
    """
    UPDATE res_currency SET active = FALSE
      WHERE name NOT IN ('EUR', 'CHF', 'USD')
    """


  @company
  Scenario: Configure main partner and company
  Given I find a "res.company" with oid: base.main_company
    And having:
         | key                       | value        |
         | name                      | QoQa Holding |
         | expects_chart_of_accounts | false        |

    Given the company has the "images/logo_qoqa_ch.png" logo
    And the company currency is "CHF" with a rate of "1.00"

  @user_admin
  Scenario: Assign groups concerning the accounting to some users
    Given we select users below:
    | login |
    | admin |
  Then we assign all groups to the users


  @account_type
  Scenario: importing Chart of account from CSV
    Given "account.account.type" is imported from CSV "setup/type_de_compte.csv" using delimiter ","


  @l10n_ch_payment_slip_voucher_disable
  Scenario: DISABLE VOUCHER FOR L10N_CH_PAYMENT_SLIP
    Given I need a "ir.config_parameter" with oid: l10n_ch_payment_slip.payment_slip_voucher_disable
    And having:
    | name  | value                                |
    | value | 1                                    |

  @mail_setup_incoming
  Scenario: CREATE THE INCOMING MAIL SERVER
    Given I need a "fetchmail.server" with oid: scenario.openerp_incomming_claim
    And having:
    | name       | value                                |
    | name       | openerp_incomming_claim              |
    And I test and confirm the incomming mail server

  @mail_setup_outgoing
  Scenario: CREATE THE OUTGOING MAIL SERVER
    Given I need a "ir.mail_server" with oid: scenario.openerp_smtp_server
    And having:
    | name       | value                                |
    | name       | openerp_smtp_server                  |
    | sequence   | 1                                    |

  @setup_domain
  Scenario: CREATE THE DOMAIN
    Given I need a "base.config.settings" with oid: scenario.openerp_domain
    And having:
    | name               | value                 |
    | alias_domain       | qoqa.com              |

