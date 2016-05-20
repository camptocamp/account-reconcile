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
      | specific_fct                               |
      | purchase_analytic_global                   |
      | purchase_variant_fast_entry                |
      | crm_rma_stock_location                     |
      | stock_orderpoint_generator                 |
      | stock_location_search_stock                |
      | stock_picking_mass_assign                  |
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
    SET claim_sale_order_regexp = '<b>Order :</b>\s*<a href="http[^"]+"[^>]*>(\d+)</a>'
    """

    Given I find a "mass.object" with name: Bon de livraison
    And I add the date_expected field to the mass editing

    Given I find a possibly inactive "ir.cron" with oid: picking_dispatch.ir_cron_dispatch_check_assign_all
    And having:
      | name   | value                                  |
      | active | false                                  |
      | args   | (None, [("state", "=", "assigned")])   |

    Given I find a possibly inactive "ir.cron" with oid: stock_picking_mass_assign.ir_cron_check_assign_all
    And having:
      | name            | value                         |
      | active          | true                          |
      | interval_number | 4                             |

    Given I execute the SQL commands
    """
    UPDATE procurement_order p
    SET offer_id = so.offer_id
    FROM sale_order_line sol, sale_order so
    WHERE sol.procurement_id = p.id
    AND so.id = sol.order_id
    AND so.offer_id IS NOT NULL
    AND p.offer_id IS NULL
    """

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
