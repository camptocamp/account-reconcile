# -*- coding: utf-8 -*-
@upgrade_1.1.0 @qoqa

Feature: upgrade to 1.1.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | connector_qoqa                             |
      | qoqa_base_data                             |
      | crm_claim_mail                             |
      | qoqa_offer                                 |
      | stock_picking_update_date                  |
      | picking_dispatch                           |
      | delivery_carrier_label_dispatch            |
      | picking_dispatch_delay_done                |
    Then my modules should have been installed and models reloaded

    Given I find a "payment.method" with oid: scenario.payment_method_paypal_ch
    And having:
      | key                         | value |
      | payment_cancellable_on_qoqa | false |
    Given I find a "payment.method" with oid: scenario.payment_method_paypal_fr
    And having:
      | key                         | value |
      | payment_cancellable_on_qoqa | false |

    Given I execute the SQL commands
    """
    UPDATE res_company
    SET claim_sale_order_regexp = '\*\*\* Numéro de commande : (\d+) \*\*\*'
    """

    Given I find a "mass.object" with name: Bon de livraison
    And I add the field with oid stock_picking_update_date.field_stock_picking_date_expected_5267 to the mass editing

    Given I find a possibly inactive "ir.cron" with oid: picking_dispatch.ir_cron_dispatch_check_assign_all
    And having:
      | name   | value                                  |
      | active | true                                   |
      | args   | '(None, [("state", "=", "assigned")])' |

    Given I set the version of the instance to "1.1.0"
