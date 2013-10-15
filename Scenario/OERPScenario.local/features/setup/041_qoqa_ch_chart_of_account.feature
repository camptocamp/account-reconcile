@setup
Feature: QoQa CH account chart
  @account_chart
  Scenario: importing Chart of account from CSV
    Given I am configuring the company with ref "scenario.qoqa_ch"
    And Create external ids for accounts from "setup/QoQa_ERP_Plan_comptable_v2_c2c.csv"
    And "account.account" is imported from CSV "setup/QoQa_ERP_Plan_comptable_v2_c2c.csv" using delimiter ";"
