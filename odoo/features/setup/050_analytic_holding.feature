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

Feature: ANALYTIC SETTING FOR QOQA HOLDING
   As an administrator, I do the following installation steps.

##### ANALYTIC JOURNALS CREATION ####
  @analytic_journal_holding
  Scenario Outline: ANALYTIC JOURNALS
    Given I need a "account.analytic.journal" with oid: <oid>
      And having:
        | name       | value                     |
        | company_id | by oid: base.main_company |
        | name       | <name>                    |
        | type       | <type>                    |
        | code       | <code>                    |

  Examples: Create the following analytic journals
        | oid                                       | name      | type     | code |
        | scenario.analytic_journal_general_holding | General   | general  | GEN  |
