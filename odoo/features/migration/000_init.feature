# -*- coding: utf-8 -*-
###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2016 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@migration @9.0

Feature: Parameter the new database
  In order to have a coherent installation
  I've automated the manual steps.

  @no_login
  Scenario: CREATE DATABASE
    Given I find or create database from config file

  @modules
  Scenario: install modules
    Given I install the required modules with dependencies:
        | name                                            |
        #---- Base ---------------------------------------#
        | account                                         |
        | base_import                                     |
        | document                                        |
        | stock                                           |
        | sale                                            |
        | l10n_ch                                         |
        | l10n_fr                                         |
        | l10n_multilang                                  |
        # old official modules
        #| multi_company                                   |
        #---- OCA/account-financial-reporting ------------#
        #| account_export_csv                              |
        #| account_financial_report_webkit [DEPRECATED]    |
        #---- OCA/account-financial-tools ----------------#
        #| account_constraints                             |
        #| account_default_draft_move                      |
        | account_permanent_lock_move                     |
        #| account_reversal                                |
        #| currency_rate_update                            |
        #---- OCA/account-fiscal-rule --------------------#
        #| account_fiscal_position_rule                    |
        #| account_fiscal_position_rule_sale               |
        #---- OCA/account-invoice-reporting --------------#
        #| invoice_webkit [DEPRECATED]                     |
        #---- OCA/bank-payment ---------------------------#
        | account_payment_mode                            |
        | account_payment_sale                            |
        #---- OCA/bank-statement-reconcile ---------------#
        | account_mass_reconcile                          |
        | account_move_base_import                        |
        | account_move_transactionid_import               |
        | base_transaction_id                             |
        #| invoicing_voucher_killer [DEPRECATED]           |
        #| statement_voucher_killer [DEPRECATED]           |
        #---- OCA/carrier-delivery -----------------------#
        | base_delivery_carrier_label                     |
        | delivery_carrier_label_postlogistics            |
        | delivery_carrier_label_postlogistics_shop_logo  |
        #---- OCA/connector-ecommerce --------------------#
        #| connector_ecommerce                             |
        #---- OCA/crm ------------------------------------#
        | crm_claim_merge                                 |
        #---- OCA/margin-analysis ------------------------#
        #| product_cost_incl_bom                           |
        #| product_cost_incl_bom_price_history             |
        #| product_get_cost_field                          |
        #| product_historical_margin                       |
        #| product_price_history                           |
        #| product_standard_margin                         |
        #| product_stock_cost_field_report                 |
        #---- OCA/l10n-france ----------------------------#
        #| l10n_fr_rib                                     |
        #---- OCA/l10n-switzerland -----------------------#
        | l10n_ch_bank                                    |
        | l10n_ch_base_bank                               |
        #| l10n_ch_dta                                     |
        | l10n_ch_payment_slip                            |
        | l10n_ch_zip                                     |
        #---- OCA/product-attributes ---------------------#
        | product_brand                                   |
        #---- OCA/purchase-workflow ----------------------#
        | purchase_discount                               |
        #| purchase_landed_costs                           |
        #---- OCA/rma ------------------------------------#
        | crm_claim_rma                                   |
        | crm_rma_stock_location                          |
        #---- OCA/sale-reporting -------------------------#
        #| sale_order_webkit                               |
        #| sale_jit_on_services                            |
        #---- OCA/sale-workflow  -------------------------#
        | sale_automatic_workflow                         |
        | sale_automatic_workflow_payment_mode            |
        #---- OCA/server-tools ---------------------------#
        | mail_cleanup                                    |
        | mail_environment                                |
        #---- OCA/stock-logistics-warehouse --------------#
        | stock_orderpoint_generator                      |
        #---- OCA/stock-logistics-workflow ---------------#
        #| picking_dispatch                                |
        #---- OCA/web ------------------------------------#
        | web_send_message_popup                          |
        #| web_translate_dialog                            |
        #---- QoQa specifics -----------------------------#
        #| base_stock_picking_pack_split                   |
        #| connector_file_s3_import                        |
        #| connector_qoqa                                  |
        #| crm_claim_mail                                  |
        | crm_rma_by_shop                                  |
        #| delivery_carrier_label_swiss_pp                 |
        #| delivery_carrier_url                            |
        #| ecotax                                          |
        | picking_dispatch_delay_done                     |
        #| picking_dispatch_group                          |
        #| purchase_variant_fast_entry                     |
        #| qoqa_base_data                                  |
        #| qoqa_claim                                      |
        #| qoqa_label_dispatch_pack_split                  |
        #| qoqa_offer                                      |
        #| qoqa_offer_historical_margin                    |
        | qoqa_product                          |
        | qoqa_record_archiver                            |
        #| server_env_connector_qoqa                       |
        #| specific_fct                                    |
        #| specific_report                                 |
        #| web_custom                                      |
        | web_environment |
        #| wine_ch_report                                  |
    Then my modules should have been installed and models reloaded

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
         | key      | value    |
         | grouping | [3, 0]   |
         | name     | Français |
    Given I find a "res.lang" with code: de_DE
    And having:
         | key      | value   |
         | grouping | [3, 0]  |
         | name     | Deutsch |

  @currencies
  Scenario: Activate currencies
    Given  I execute the SQL commands
    """
    UPDATE res_currency SET active = TRUE
      WHERE name IN ('EUR', 'CHF', 'USD')
    """

  @company
  Scenario: Configure main partner and company
  Given I find a "res.company" with oid: base.main_company
    And having:
         | key                       | value        |
         | name                      | QoQa Holding |
         | currency_id               | by name: CHF |
    Given the company has the "images/logo_qoqa_ch.png" logo
