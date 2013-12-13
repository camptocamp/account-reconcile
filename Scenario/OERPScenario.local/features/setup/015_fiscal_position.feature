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
@fiscal_position @setup

Feature: Create fiscal position and fiscal position rules

  @position @vat @ch
  Scenario: Create the fiscal position for 8.0% → 7.6%
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I need a "account.fiscal.position" with oid: scenario.fiscalpos_76
    And having:
      | key        | value                             |
      | name       | TVA 7.6% avant 2011               |
      | company_id | by oid: scenario.qoqa_ch          |
      | active     | True                              |
    Given I need a "account.fiscal.position.tax" with oid: scenario.fiscalpos_tax_76
    And having:
      | key         | value                         |
      | position_id | by oid: scenario.fiscalpos_76 |
      | tax_src_id  | by description: 8.0%          |
      | tax_dest_id | by description: 7.6%          |

  @rule @vat @ch
  Scenario: Create the fiscal position rule for 8.0% → 7.6%
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I need a "account.fiscal.position.rule" with oid: scenario.fiscalpos_rule_76
    And having:
      | key                | value                                     |
      | name               | TVA 7.6% avant 2011                       |
      | description        | Changement de TVA en Suisse au 01.01.2011 |
      | company_id         | by oid: scenario.qoqa_ch                  |
      | date_end           | 2010-12-31                                |
      | use_sale           | True                                      |
      | fiscal_position_id | by oid: scenario.fiscalpos_76             |

  @position @vat @fr
  Scenario: Create the fiscal position for 20.0% → 19.6%
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I need a "account.fiscal.position" with oid: scenario.fiscalpos_196
    And having:
      | key        | value                             |
      | name       | TVA 19.6% avant 2014              |
      | company_id | by oid: scenario.qoqa_fr          |
      | active     | True                              |
    Given I need a "account.fiscal.position.tax" with oid: scenario.fiscalpos_tax_196
    And having:
      | key         | value                          |
      | position_id | by oid: scenario.fiscalpos_196 |
      | tax_src_id  | by description: 20.0           |
      | tax_dest_id | by description: 19.6           |

  @rule @vat @fr
  Scenario: Create the fiscal position rule for 20.0% → 19.6%
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I need a "account.fiscal.position.rule" with oid: scenario.fiscalpos_rule_196
    And having:
      | key                | value                                     |
      | name               | TVA 19.6% avant 2014                      |
      | description        | Changement de TVA en France au 01.01.2014 |
      | company_id         | by oid: scenario.qoqa_fr                  |
      | date_end           | 2014-12-31                                |
      | use_sale           | True                                      |
      | fiscal_position_id | by oid: scenario.fiscalpos_196            |


  @historic_account_tax
  Scenario: I set the historic account taxes for CH (7.6%,3.6%,2.4%) as inactiv
    Given I need a "account.tax" with oid: scenario.vat_76
    And having
         | key                  | value                                                           |
         | active               | False                                                            |
    Given I need a "account.tax" with oid: scenario.vat_36
    And having
         | key                  | value                                                           |
         | active               | False                                                            |
    Given I need a "account.tax" with oid: scenario.vat_24
    And having
         | key                  | value                                                           |
         | active               | False                                                            |