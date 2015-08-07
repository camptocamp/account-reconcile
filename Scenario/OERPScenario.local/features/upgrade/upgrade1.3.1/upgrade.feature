# -*- coding: utf-8 -*-
@upgrade_from_1.3.0 @qoqa

Feature: upgrade to 1.3.1

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | account_advanced_reconcile_ref_deep_search |
      | specific_fct                               |
    Then my modules should have been installed and models reloaded

  Scenario: add reconciliation methods
    Given I need a "account.easy.reconcile" with oid: scenario.reconcile_20400
    And having:
      | key        | value                         |
      | name       | 20400 Bons Cadeau             |
      | account    | by oid: scenario.pcg_CH_20400 |
      | company_id | by oid: scenario.qoqa_ch      |

    Given I need a "account.easy.reconcile.method" with oid: scenario.reconcile_deep_search_20400
    And having:
      | key                 | value                                   |
      | name                | easy.reconcile.advanced.ref.deep.search |
      | account_profit_id   | by name: Différences d'arrondis         |
      | account_lost_id     | by name: Différences d'arrondis         |
      | analytic_account_id | by code: AA007                          |
      | company_id          | by oid: scenario.qoqa_ch                |
      | date_base_on        | newest                                  |
      | journal_id          | by id: 6                                |
      | sequence            | 1                                       |
      | task_id             | by oid: scenario.reconcile_20400        |
      | write_off           | 0.01                                    |

    Given I need a "account.easy.reconcile.method" with oid: scenario.reconcile_deep_search_20410
    And having:
      | key                 | value                                   |
      | name                | easy.reconcile.advanced.ref.deep.search |
      | account_profit_id   | by name: Différences d'arrondis         |
      | account_lost_id     | by name: Différences d'arrondis         |
      | analytic_account_id | by code: AA007                          |
      | company_id          | by oid: scenario.qoqa_ch                |
      | date_base_on        | newest                                  |
      | journal_id          | by id: 6                                |
      | sequence            | 1                                       |
      | task_id             | by name: 20410 Bons de Rabais           |
      | write_off           | 0.01                                    |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.3.1"
