# -*- coding: utf-8 -*-
@upgrade_from_1.0.46 @qoqa

Feature: upgrade to 1.0.47

  Scenario: I configure the new credentials for La Poste
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | name                                | value                       |
      | postlogistics_username              | TUW003061	                  |
      | postlogistics_password              | %xnYKO.{e~V9                |

    Given I set the version of the instance to "1.0.47"
