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
        | name                           |
        | account                        |
        | multi_company                  |
        | base_import                    |
        | l10n_ch                        |
        | l10n_ch_base_bank              |
        | l10n_ch_zip                    |
        | l10n_ch_dta                    |
        | l10n_ch_payment_slip           |
        | l10n_fr                        |
        | stock                          |
        | sale                           |
        | sale_order_webkit              |
        | connector_ecommerce            |
        | connector_qoqa                 |
        | purchase_landed_costs          |
        | product_multi_company          |
        | crm_claim_rma                  |
        | specific_fct                   |
        | product_custom_attributes      |
        | wine_ch_report                 |
        | discount_coupon                |
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
