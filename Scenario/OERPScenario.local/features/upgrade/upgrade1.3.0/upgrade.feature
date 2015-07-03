# -*- coding: utf-8 -*-
@upgrade_from_1.2 @qoqa

Feature: upgrade to 1.3.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | connector_file                   |
      | server_env_connector_file        |
    Then my modules should have been installed and models reloaded

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

    Given I set the version of the instance to "1.3.0"
