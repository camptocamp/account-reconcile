# -*- coding: utf-8 -*-
@upgrade_from_1.0.54 @qoqa

Feature: upgrade to 1.1.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | picking_dispatch                           |
      | delivery_carrier_label_dispatch            |
    Then my modules should have been installed and models reloaded

    Given I find a possibly inactive "ir.cron" with oid: picking_dispatch.ir_cron_dispatch_check_assign_all
    And having:
      | name   | value                                  |
      | active | true                                   |
      | args   | '(None, [("state", "=", "assigned")])' |

    Given I set the version of the instance to "1.1.0"
