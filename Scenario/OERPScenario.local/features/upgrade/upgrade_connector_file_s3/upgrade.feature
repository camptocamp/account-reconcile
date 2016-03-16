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
    | name               | PostFinance CCP                          |
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
    | delimiter                 | ,                                        |
    | quotechar                 | "                                        |

  Scenario: add Amex import profile
    Given I need a "file_import.backend" with oid: scenario.file_import_backend_amex
    And having:
    | key                       | value                                           |
    | name                      | American Express                                |
    | version                   | s3_1                                            |
    | company_id                | by oid: scenario.qoqa_ch                        |
    | user_id                   | by oid: connector_qoqa.user_connector_ch        |
    | bank_statement_profile_id | by oid: __export__.account_statement_profile_45 |
    | delimiter                 | ,                                               |
    | quotechar                 | "                                               |

  Scenario: add Postfinance import profile
    Given I need a "file_import.backend" with oid: scenario.file_import_backend_postfinance2
    And having:
    | key                       | value                                           |
    | name                      | PostFinance                                     |
    | version                   | s3_1                                            |
    | company_id                | by oid: scenario.qoqa_ch                        |
    | user_id                   | by oid: connector_qoqa.user_connector_ch        |
    | bank_statement_profile_id | by oid: scenario.profile_import_cb_postfinance  |
    | delimiter                 | ,                                               |
    | quotechar                 | "                                               |

  Scenario: add Visa MasterCard import profile
    Given I need a "file_import.backend" with oid: scenario.file_import_backend_fix
    And having:
    | key                       | value                                              |
    | name                      | Visa MasterCard                                    |
    | version                   | s3_1                                               |
    | company_id                | by oid: scenario.qoqa_ch                           |
    | user_id                   | by oid: connector_qoqa.user_connector_ch           |
    | bank_statement_profile_id | by oid: scenario.profile_import_visa_mastercard_ch |
    | delimiter                 | ,                                                  |
    | quotechar                 | "                                                  |

  Scenario: add SwissBilling import profile
    Given I need a "file_import.backend" with oid: scenario.file_import_backend_swissbilling
    And having:
    | key                       | value                                              |
    | name                      | SwissBilling                                       |
    | version                   | s3_1                                               |
    | company_id                | by oid: scenario.qoqa_ch                           |
    | user_id                   | by oid: connector_qoqa.user_connector_ch           |
    | bank_statement_profile_id | by oid: __export__.account_statement_profile_37    |
    | delimiter                 | ,                                                  |
    | quotechar                 | "                                                  |
