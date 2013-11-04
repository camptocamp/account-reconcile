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

Feature: PRE-DEFINED USERS FOR TEST INSTANCE TO REPLACE BY USER FOR GO LIVE
   As an administrator, I do the following installation steps.

  @analytic_account_ch
  Scenario Outline: Create an analytic account
     Given I need a "account.analytic.account" with name: <name>
       And having:
        | name       | value                    |
        | type       | normal                   |
        | company_id | by oid: scenario.qoqa_ch |

  Examples: Create the following analytic accounts
        | name   |
        | Ventes |
        | Achats |
        | Autres |

##### ANALYTIC JOURNALS CREATION ####
  @analytic_journal
  Scenario Outline: ANALYTIC JOURNALS
    Given I need a "account.analytic.journal" with oid: <oid>
      And having:
        | name       | value                     |
        | company_id | by oid: base.main_company |
        | name       | <name>                    |
        | type       | <type>                    |
        | code       | <code>                    |

  Examples: Create the following analytic journals
        | oid                                   | name      | type     | code |
        | scenario.analytic_journal_sale_ch     | Sales     | sale     | SAL  |
        | scenario.analytic_journal_purchase_ch | Purchases | purchase | PUR  |


  @link_financial_journals_ch
  Scenario Outline: FINANCIAL JOURNALS CREATION
    Given there is a journal with name "<journal_name>" and company "QoQa Services SA"
      And having:
        | name                      | value                       |
        | analytic_journal_id       | by oid: <analytic_journal> |

   Examples:
         | journal_name            | analytic_journal                      |
         | Sales Journal           | scenario.analytic_journal_sale_ch     |
         | Sales Refund Journal    | scenario.analytic_journal_sale_ch     |
         | Purchase Journal        | scenario.analytic_journal_purchase_ch |
         | Purchase Refund Journal | scenario.analytic_journal_purchase_ch |
