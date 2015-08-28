# -*- coding: utf-8 -*-
@upgrade_from_1.3.3 @qoqa

Feature: upgrade to 1.3.4

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | account_export_csv                         |
      | account_financial_report_webkit            |
      | account_financial_report_webkit_xls        |
      | connector_qoqa                             |
      | specific_fct                               |
      | specific_report                            |
    Then my modules should have been installed and models reloaded

  Scenario: create partner for claim response
  Given I need a "res.partner" with oid: scenario.loutres_qoqa_ch_fr
    And having:
         | key        | value                     |
         | name       | Loutres                   |
         | company_id | by oid: base.main_company |
         | active     | True                      |
         | email      | loutres@qoqa.com          |

  Scenario: re-export categories
    Given I re-export to QoQa the product categories

  Scenario: upgrade application version
    Given I set the version of the instance to "1.3.4"
