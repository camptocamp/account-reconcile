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
@core_setup

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
        | l10n_ch                        |
        | stock                          |
        | sale                           |
        | sale_order_webkit              |
        | sale_validity                  |
        | sale_stock_prebook             |
        | sale_ownership                 |
        | purchase                       |
        | mail                           |
        | purchase_extended              |
        | purchase_requisition_extended  |
        | transport_plan                 |
        | logistic_requisition           |
        | logistic_order                 |
        | document                       |
        | sale_exceptions                |
        | stock_split_picking            |
        | sale_cancel_reason             |
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
   Then the language should be available
    Given I find a "res.lang" with code: en_US
    And having:
         | key      | value  |
         | grouping | [3, 0] |
    Given I find a "res.lang" with code: fr_FR
    And having:
         | key      | value  |
         | grouping | [3, 0] |

  @company
  Scenario: Configure main partner and company
  Given I find a "res.company" with oid: base.main_company
    And having:
         | key        | value                      |
         | name       | GAIN                       |
         | street     | Rue de Vermont 37-39       |
         | street2    |                            |
         | zip        | 1202                       |
         | city       | Geneva                     |
         | country_id | by code: CH                |
         | phone      | +41 22 749 1850            |
         | fax        | +41 22 749 1851            |
         | email      |                            |
         | website    | http://www.gainhealth.org/ |

    Given the company has the "images/logo.jpg" logo
    And the company currency is "CHF" with a rate of "1.00"
    Given I need a "res.partner" with oid: scenario.partner_gain
    And having:
       | key        | value                                                    |
       | name       | Fédération internationale des Sociétés de la Croix-Rouge |
       | lang       | en_US                                                    |
       | website    | http://ifrc.org/                                         |
       | customer   | false                                                    |
       | supplier   | false                                                    |
       | street     | Chemin des Crêts, 17                                     |
       | street2    | Petit-Saconnex                                           |
       | zip        | 1211                                                     |
       | city       | Genève                                                   |
       | country_id | by code: CH                                              |
       | phone      | +41 22 730 42 22                                         |
       | fax        | +41 22 733 03 95                                         |
       | email      |                                                          |
       | is_company | True                                                     |
       | company_id | by id: 1                                                 |

  @user_admin
  Scenario: Assign groups concerning the accounting to some users
    Given we select users below:
    | login |
    | admin |
  Then we assign all groups to the users

   @defaults
   Scenario: Create default values (ir.values)
      Given I load the data file "setup/purchase.requisition.yml"
