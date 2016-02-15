# -*- coding: utf-8 -*-
@upgrade_connector_file_s3 @qoqa

Feature: add connector file

  Scenario: upgrade application version

    Given I update the module list
    Given I uninstall the following modules
      | name                      |
      | server_env_connector_file |
    Given I install the required modules with dependencies:
      | name                     |
      | connector_file_s3_import |
    Then my modules should have been installed and models reloaded

  Scenario: update Postfinance import profile
    Given I need a "file_import.backend" with oid: scenario.file_import_backend_postfinance
    And having:
    | key                | value                                    |
    | name               | Postfinance                              |
    | version            | s3_1                                     |
    | delimiter          | ,                                        |
    | quotechar          | "                                        |

  Scenario: add Paypal import profile
    Given I need a "file_import.backend" with oid: scenario.file_import_backend_paypal
    And having:
    | key                       | value                                    |
    | name                      | Paypal                                   |
    | version                   | s3_1                                     |
    | company_id                | by oid: scenario.qoqa_ch                 |
    | user_id                   | by oid: connector_qoqa.user_connector_ch |
    | bank_statement_profile_id | by oid: scenario.profile_paypal_ch       |
    | delimiter                 | ;                                        |
    | quotechar                 | "                                        |
