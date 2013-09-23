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
@qoqa_fr @core_setup

Feature: Configure QoQa.fr

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
    And the company currency is "EUR" with a rate of "0.811035"

  @qoqa_fr_logistics
  Scenario: configure logistics
    Given I need a "stock.location" with oid: scenario.stock_location_company_fr
    And having:
    | name        | value                       |
    | name        | QoQa Services France        |
    | usage       | view                        |
    | location_id | by name: Physical Locations |
    | company_id  | by oid: scenario.qoqa_fr    |
    Given I need a "stock.location" with oid: scenario.stock_location_output_fr
    And having:
    | name                  | value                                      |
    | name                  | Output                                     |
    | usage                 | internal                                   |
    | location_id           | by oid: scenario.stock_location_company_fr |
    | chained_location_id   | by name: Customers                         |
    | chained_location_type | customer                                   |
    | chained_auto_packing  | transparent                                |
    | chained_picking_type  | out                                        |
    | chained_journal_id    | by name: Delivery Orders                   |
    | company_id            | by oid: scenario.qoqa_fr                   |
    Given I need a "stock.location" with oid: scenario.stock_location_stock_fr
    And having:
     | name        | value                                      |
     | name        | Stock                                      |
     | company_id  | by oid: scenario.qoqa_fr                   |
     | usage       | internal                                   |
     | location_id | by oid: scenario.stock_location_company_fr |
    Given I need a "stock.location" with oid: scenario.location_fr_sav
    And having:
    | name        | value                                      |
    | name        | SAV                                        |
    | location_id | by oid: scenario.stock_location_company_fr |
    | company_id  | by oid: scenario.qoqa_fr                   |
    Given I need a "stock.location" with oid: scenario.location_fr_non_reclame
    And having:
    | name        | value                                      |
    | name        | Non réclamé                                |
    | location_id | by oid: scenario.stock_location_company_fr |
    | company_id  | by oid: scenario.qoqa_fr                   |
    Given I need a "stock.location" with oid: scenario.location_fr_defectueux
    And having:
    | name        | value                                      |
    | name        | Défectueux                                 |
    | location_id | by oid: scenario.stock_location_company_fr |
    | company_id  | by oid: scenario.qoqa_fr                   |
    Given I need a "stock.warehouse" with oid: scenario.warehouse0
    And having:
    | name          | value                                     |
    | name          | QoQa Services France                      |
    | lot_input_id  | by oid: scenario.stock_location_stock_fr  |
    | lot_output_id | by oid: scenario.stock_location_output_fr |
    | lot_stock_id  | by oid: scenario.stock_location_stock_fr  |
    | company_id    | by oid: scenario.qoqa_fr                  |
    Given I need a "sale.shop" with oid: sale.sale_shop_fr
    And having:
    | name       | value                    |
    | name       | QoQa Services SA         |
    | company_id | by oid: scenario.qoqa_fr |
