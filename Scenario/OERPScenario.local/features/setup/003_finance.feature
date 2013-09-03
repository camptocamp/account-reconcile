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

Feature: Setup the finance for GAIN

  @account_chart
  Scenario: Generate account chart
    Given I have the module account installed
    And I want to generate account chart from chart template named "Plan comptable STERCHI" with "4" digits for company "GAIN"
    When I generate the chart
    Then accounts should be available for company "GAIN"

  @fiscalyear
    Scenario: create fiscal years
    Given I need a "account.fiscalyear" with oid: scenario.fy2013
    And having:
    | name       |      value |
    | name       |       2013 |
    | code       |       2013 |
    | date_start | 2013-01-01 |
    | date_stop  | 2013-12-31 |
    And I create monthly periods on the fiscal year with reference "scenario.fy2013"
    Then I find a "account.fiscalyear" with oid: scenario.fy2013
