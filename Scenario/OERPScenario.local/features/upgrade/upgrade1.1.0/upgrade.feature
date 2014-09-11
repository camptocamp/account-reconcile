# -*- coding: utf-8 -*-
@upgrade_1.1.0 @qoqa

Feature: upgrade to 1.1.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | crm_rma_stock_location                     |
    Then my modules should have been installed and models reloaded

    Given I find a "stock.warehouse" with oid: stock.warehouse0
    And having:
      | name       | value                            |
      | lot_rma_id | by oid: scenario.location_ch_sav |

    Given I find a "stock.warehouse" with oid: scenario.warehouse_fr
    And having:
      | name       | value                            |
      | lot_rma_id | by oid: scenario.location_fr_sav |

    Given I find a "stock.location" with oid: crm_rma_stock_location.stock_location_rma
    And having:
      | name       | value                            |
      | active     | false                            |

    Given I set the version of the instance to "1.1.0"
