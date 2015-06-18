# -*- coding: utf-8 -*-
@upgrade_from_1.2 @qoqa

Feature: upgrade to 1.3.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
      | record_archiver                  |
    Then my modules should have been installed and models reloaded

  Scenario Outline: setup cron to archive old records
    Given I need a "record.lifespan" with oid: scenario.lifespan_<oid>
    And having:
      | name       | value                    |
      | model_id   | by model: <model>        |
      | months     | <months>                 |
  Examples:
      | oid              | model            | months |
      | sale_order       | sale.order       | 24     |
      | qoqa_offer       | qoqa.offer       | 6      |
      | stock_picking    | stock.picking    | 3      |
      | picking_dispatch | picking.dispatch | 3      |
      | purchase_order   | purchase.order   | 6      |
      | account_invoice  | account.invoice  | 24     |
      | crm_claim        | crm.claim        | 24     |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.3.0"
