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

Feature: ANALYTIC SETTING FOR QOQA CH
   As an administrator, I do the following installation steps.

  @analytic_account_shop_ch
   Scenario: Create the ch root analytic account

    Given I need a "account.analytic.account" with oid: scenario.qoqa_ch_root_aa
      And having:
        | name       | value                    |
        | name       | QoQa Suisse              |
        | type       | view                     |
        | company_id | by oid: scenario.qoqa_ch |
        | currency_id | by name: CHF            |

  Scenario Outline: Create an analytic account
    Given I need a "account.analytic.account" with oid: <oid>
      And having:
        | name        | value                            |
        | name        | <name>                           |
        | type        | normal                           |
        | parent_id   | by oid: scenario.qoqa_ch_root_aa |
        | company_id  | by oid: scenario.qoqa_ch         |
        | currency_id | by name: CHF                     |

      Examples: Create an analytic accounts per shop
        | oid                                       | name       |
        | scenario.analytic_account_shop_qoqa_ch    | QoQa.ch    |
        | scenario.analytic_account_shop_qwine_ch   | Qwine.ch   |
        | scenario.analytic_account_shop_qsport_ch  | Qsport.ch  |
        | scenario.analytic_account_shop_qstyle_ch  | Qstyle.ch  |
        | scenario.analytic_account_shop_qooking_ch | Qooking.ch |
        | scenario.analytic_account_shop_general_ch | General    |

  @sale_shop_analytic_account_ch
  Scenario Outline: Configure sale shops' analytic account
    Given I find a "sale.shop" with oid: <oid>
      And having:
        | name       | value                      |
        | project_id | by oid: <analytic_account> |

      Examples: Shops
        | oid                            | analytic_account                          |
        | qoqa_base_data.shop_qoqa_ch    | scenario.analytic_account_shop_qoqa_ch    |
        | qoqa_base_data.shop_qwine_ch   | scenario.analytic_account_shop_qwine_ch   |
        | qoqa_base_data.shop_qstyle_ch  | scenario.analytic_account_shop_qsport_ch  |
        | qoqa_base_data.shop_qsport_ch  | scenario.analytic_account_shop_qstyle_ch  |
        | qoqa_base_data.shop_qooking_ch | scenario.analytic_account_shop_qooking_ch |
        | qoqa_base_data.shop_general_ch | scenario.analytic_account_shop_general_ch |

##### ANALYTIC JOURNALS CREATION ####
  @analytic_journal_ch
  Scenario Outline: ANALYTIC JOURNALS
    Given I need a "account.analytic.journal" with oid: <oid>
      And having:
        | name       | value                    |
        | company_id | by oid: scenario.qoqa_ch |
        | name       | <name>                   |
        | type       | <type>                   |
        | code       | <code>                   |

  Examples: Create the following analytic journals
        | oid                                   | name      | type     | code |
        | scenario.analytic_journal_sale_ch     | Sales     | sale     | SAL  |
        | scenario.analytic_journal_purchase_ch | Purchases | purchase | PUR  |
        | scenario.analytic_journal_general_ch  | General   | general  | GEN  |


  @link_financial_journals_ch
  Scenario Outline: FINANCIAL JOURNALS CREATION
    Given there is a journal with name "<journal_name>" and company "QoQa Services SA"
      And having:
        | name                      | value                      |
        | analytic_journal_id       | by oid: <analytic_journal> |

   Examples:
         | journal_name            | analytic_journal                      |
         | Sales Journal           | scenario.analytic_journal_sale_ch     |
         | Sales Refund Journal    | scenario.analytic_journal_sale_ch     |
         | Purchase Journal        | scenario.analytic_journal_purchase_ch |
         | Purchase Refund Journal | scenario.analytic_journal_purchase_ch |
         | Miscellaneous Journal   | scenario.analytic_journal_general_ch  |
