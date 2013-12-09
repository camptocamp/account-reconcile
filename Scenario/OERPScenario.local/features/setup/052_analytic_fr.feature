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
@analytic @setup

Feature: ANALYTIC SETTING FOR QOQA FR
   As an administrator, I do the following installation steps.

  @analytic_account_shop_fr
   Scenario: Create the fr root analytic account
    Given I need a "account.analytic.account" with oid: scenario.qoqa_fr_root_aa
      And having:
        | name       | value                    |
        | name       | QoQa France              |
        | type       | view                     |
        | company_id | by oid: scenario.qoqa_fr |
  Scenario Outline: Create an analytic account
    Given I need a "account.analytic.account" with oid: <oid>
      And having:
        | name       | value                    |
        | name       | <name>                   |
        | type       | normal                   |
        | parent_id  | by oid: scenario.qoqa_fr_root_aa |
        | company_id | by oid: scenario.qoqa_fr |

  Examples: Create an analytic accounts per shop
        | oid                                     | name     |
        | scenario.analytic_account_shop_qoqa_fr  | QoQa.fr  |
        | scenario.analytic_account_shop_qwine_fr | Qwine.fr |

  @sale_shop_analytic_accounts_fr
  Scenario Outline: Configure sale shops' analytic account
    Given I find a "sale.shop" with oid: <oid>
      And having:
        | name       | value                      |
        | project_id | by oid: <analytic_account> |

      Examples: Shops
        | oid                          | analytic_account                        |
        | qoqa_base_data.shop_qoqa_fr  | scenario.analytic_account_shop_qoqa_fr  |
        | qoqa_base_data.shop_qwine_fr | scenario.analytic_account_shop_qwine_fr |

##### ANALYTIC JOURNALS CREATION ####
  @analytic_journal_fr
  Scenario Outline: ANALYTIC JOURNALS
    Given I need a "account.analytic.journal" with oid: <oid>
      And having:
        | name       | value                     |
        | company_id | by oid: scenario.qoqa_fr  |
        | name       | <name>                    |
        | type       | <type>                    |
        | code       | <code>                    |

  Examples: Create the following analytic journals
        | oid                                   | name      | type     | code |
        | scenario.analytic_journal_sale_fr     | Sales     | sale     | SAL  |
        | scenario.analytic_journal_purchase_fr | Purchases | purchase | PUR  |


  @link_financial_journals_fr
  Scenario Outline: FINANCIAL JOURNALS CREATION
    Given there is a journal with name "<journal_name>" and company "QoQa Services France"
      And having:
        | name                      | value                      |
        | analytic_journal_id       | by oid: <analytic_journal> |

   Examples:
         | journal_name            | analytic_journal                      |
         | Sales Journal           | scenario.analytic_journal_sale_fr     |
         | Sales Refund Journal    | scenario.analytic_journal_sale_fr     |
         | Purchase Journal        | scenario.analytic_journal_purchase_fr |
         | Purchase Refund Journal | scenario.analytic_journal_purchase_fr |
