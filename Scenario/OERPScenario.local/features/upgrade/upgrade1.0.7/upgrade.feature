# -*- coding: utf-8 -*-
@upgrade_from_1.0.6 @qoqa

Feature: upgrade to 1.0.7

  Scenario: upgrade
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                                                   |
      | qoqa_label_dispatch_pack_split                         |
      | base_stock_picking_pack_split                          |
      | picking_dispatch                                       |
      | picking_dispatch_grouper                               |
      | base_delivery_carrier_label                            |
      | delivery_carrier_label_default_webkit                  |
      | qoqa_offer                                             |
      | specific_report                                        |
      | l10n_ch_sepa                                           |
    Then my modules should have been installed and models reloaded

  Scenario: update application version
    Given I set the version of the instance to "1.0.7"
