# -*- coding: utf-8 -*-
@upgrade_from_1.0.45 @qoqa

Feature: upgrade to 1.0.46

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name           |
      | account_advances_reconcile |
    Then my modules should have been installed and models reloaded

  Scenario: I configure the level of commit when reconcile is performed automaticaly
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | name                                | value                       |
      | reconciliation_commit_every         | 10	                  |

    Given I set the version of the instance to "1.0.46"
