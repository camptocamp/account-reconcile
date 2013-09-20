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

Feature: Setup the finance for QoQa

  @account_chart_ch
  Scenario: Generate account chart for QoQa Services SA
    Given I have the module account installed
    And I want to generate account chart from chart template named "Plan comptable STERCHI" with "4" digits for company "QoQa Services SA"
    When I generate the chart
    Then accounts should be available for company "QoQa Services SA"

  @account_chart_fr
  Scenario: Generate account chart QoQa Services France
    Given I have the module account installed
    And I want to generate account chart from chart template named "Plan Comptable Général (France)" with "6" digits for company "QoQa Services France"
    When I generate the chart
    Then accounts should be available for company "QoQa Services France"

  @fiscalyear_ch
    Scenario: create fiscal years
    Given I need a "account.fiscalyear" with oid: scenario.fy2013_ch
    And having:
    | name       | value                    |
    | name       | 2013                     |
    | code       | 2013                     |
    | date_start | 2013-01-01               |
    | date_stop  | 2013-12-31               |
    | company_id | by oid: scenario.qoqa_ch |
    And I create monthly periods on the fiscal year with reference "scenario.fy2013_ch"
    Then I find a "account.fiscalyear" with oid: scenario.fy2013_ch

  @fiscalyear_fr
    Scenario: create fiscal years
    Given I need a "account.fiscalyear" with oid: scenario.fy2013_fr
    And having:
    | name       | value                    |
    | name       | 2013                     |
    | code       | 2013                     |
    | date_start | 2013-01-01               |
    | date_stop  | 2013-12-31               |
    | company_id | by oid: scenario.qoqa_fr |
    And I create monthly periods on the fiscal year with reference "scenario.fy2013_fr"
    Then I find a "account.fiscalyear" with oid: scenario.fy2013_fr
