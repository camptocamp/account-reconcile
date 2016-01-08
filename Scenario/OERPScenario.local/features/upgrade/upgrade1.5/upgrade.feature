# -*- coding: utf-8 -*-
@upgrade_to_1.5 @qoqa

Feature: upgrade to 1.5

  Scenario: upgrade application version

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                      |
      | connector_qoqa            |
      | connector_file            |
      | server_env_connector_file |
    Then my modules should have been installed and models reloaded

  Scenario: add Postfinance import profile
    Given I need a "file_import.backend" with oid: scenario.file_import_backend_postfinance
    And having:
    | key                | value                                    |
    | name               | Postfinance                              |
    | version            | 1                                        |
    | file_name_regexp   | .+\.csv$                                 |
    | company_id         | by oid: scenario.qoqa_ch                 |
    | user_id            | by oid: connector_qoqa.user_connector_ch |
    | ftp_input_folder   |                                          |
    | ftp_failed_folder  |                                          |
    | ftp_archive_folder |                                          |
    | delimiter          | ;                                        |
    | quotechar          | "                                        |

  Scenario: create "no job" delivery carrier
    Given I need a "delivery.carrier" with oid: scenario.carrier_nojob
    And having:
         | key        | value                                                |
         | name       | On-site delivery                                     |
         | partner_id | by oid: __export__.res_partner_8                     |
         | product_id | by oid: connector_ecommerce.product_product_shipping |
         | active     | True                                                 |
         | qoqa_type  | service                                              |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.5"
