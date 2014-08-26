# -*- coding: utf-8 -*-
@upgrade_from_1.0.44 @qoqa

Feature: upgrade to 1.0.45

  Scenario: upgrade application version
#    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                   |
      | account_easy_reconcile |
      | specific_fct	       |
    Then my modules should have been installed and models reloaded

    Given I need an "ir.cron" with oid scen.swiss_do_reconcile
    And having:
      | key             | value                           |
      | name            | Do Automatic Reconciliations CH |
      | active          | 1                               |
      | user_id         | by login: admin_ch              |
      | interval_number | 3                               |
      | interval_type   | hours                           |
      | numbercall      | -1                              |
      | doall           | 0                               |
      | model           | account.easy.reconcile          |
      | function        | run_scheduler                   |
      | args            | ()                              |

    Given I need an "ir.cron" with oid scen.france_do_reconcile
    And having:
      | key             | value                           |
      | name            | Do Automatic Reconciliations FR |
      | active          | 1                               |
      | user_id         | by login: admin_fr              |
      | interval_number | 3                               |
      | interval_type   | hours                           |
      | numbercall      | -1                              |
      | doall           | 0                               |
      | model           | account.easy.reconcile          |
      | function        | run_scheduler                   |
      | args            | ()                              |


    Given I set the version of the instance to "1.0.45"
