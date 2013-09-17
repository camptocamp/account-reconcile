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

    Given the company has the "images/logo_qoqa_ch.png" logo
    And the company currency is "CHF" with a rate of "1.00"

  @user_admin
  Scenario: Assign groups concerning the accounting to some users
    Given we select users below:
    | login |
    | admin |
  Then we assign all groups to the users
