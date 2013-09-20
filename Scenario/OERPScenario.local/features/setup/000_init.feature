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
        | connector_ecommerce            |
        | connector_qoqa                 |
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
         | name       | QoQa Holding               |

    Given the company has the "images/logo_qoqa_ch.png" logo
    And the company currency is "CHF" with a rate of "1.00"

  @company_ch
  Scenario: Configure main partner and company
  Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
         | key        | value                      |
         | name       | QoQa Services SA           |
         | street     | Rue de l'Arc-en-Ciel 14    |
         | street2    |                            |
         | zip        | 1030                       |
         | city       | Bussigny-Lausanne          |
         | country_id | by code: CH                |
         | phone      | +41 21 633 20 80           |
         | fax        | +41 21 633 20 81           |
         | email      | contact@qoqa.ch            |
         | website    | http://www.qoqa.ch         |
         | parent_id  | by oid: base.main_company  |

    Given the company has the "images/logo_qoqa_ch.png" logo
    And the company currency is "CHF" with a rate of "1.00"

  @company_fr
  Scenario: Configure main partner and company for France
  Given I need a "res.company" with oid: scenario.qoqa_fr
    And having:
         | key        | value                      |
         | name       | QoQa Services France       |
         | street     | 20 rue Georges Barres      |
         | street2    |                            |
         | zip        | 33300                      |
         | city       | Bordeaux                   |
         | country_id | by code: FR                |
         | phone      | +33 5 56 37 57 08          |
         | fax        | +33 5 56 37 57 08          |
         | email      | clients@qoqa.fr            |
         | website    | http://www.qoqa.fr         |
         | parent_id  | by oid: base.main_company  |

    Given the company has the "images/logo_qoqa_fr.png" logo
    And the company currency is "EUR" with a rate of "0.811"

  @user_admin
  Scenario: Assign groups concerning the accounting to some users
    Given we select users below:
    | login |
    | admin |
  Then we assign all groups to the users
