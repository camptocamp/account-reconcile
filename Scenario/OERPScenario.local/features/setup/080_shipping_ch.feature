# -*- coding: utf-8 -*-
###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@label  @setup

Feature: SHIPPING LABEL SETTING FOR QOQA
   As an administrator, I do the following installation steps.

  @shop_label_logo
  Scenario: I set a label logo on shops
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qoqa_ch
    And I set a postlogistics label logo from file "images/qoqa_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qwine_ch
    And I set a postlogistics label logo from file "images/qwine_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qsport_ch
    And I set a postlogistics label logo from file "images/qsport_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qstyle_ch
    And I set a postlogistics label logo from file "images/qstyle_label.png"
    Given I need a "sale.shop" with oid: qoqa_base_data.shop_qooking_ch
    And I set a postlogistics label logo from file "images/qooking_label.png"

  @postlogistics_config
  Scenario: I configure postlogistics authentification
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | name                                | value                       |
      | postlogistics_username              | TU_9272_06                  |
      | postlogistics_password              | x1KsSvyY6X                  |
      | postlogistics_license_less_1kg      | 60035471                    |
      | postlogistics_license_more_1kg      | 60035471                    |
      | postlogistics_license_vinolog       | 60035471                    |
      | postlogistics_office                | 1030 Bussigny-près-Lausanne |
      | postlogistics_default_label_layout  | by code: A7                 |
      | postlogistics_default_output_format | by code: PDF                |
      | postlogistics_default_resolution    | by code: 300                |

  @postlogistics_options_update
  Scenario: I update postlogistics services (It will take 1 minute)
    Given I am configuring the company with ref "scenario.qoqa_ch"
    And I update postlogistics services

  @carrier_postlogistics_groups
  Scenario Outline: I setup a postlogistic carrier
    Given I need a "delivery.carrier" with oid: <oid>
    And having:
     | key                            | value                                                |
     | name                           | <name>                                               |
     | partner_id                     | <partner>                                            |
     | product_id                     | by oid: connector_ecommerce.product_product_shipping |
     | qoqa_id                        | <qoqa_id>                                            |
     | active                         | <active>                                             |
     | type                           | postlogistics                                        |
     | postlogistics_service_group_id | by name: <service_name>                              |

    Examples: carrier
      | oid                                  | name    | partner                                                    | qoqa_id | active | service_name |
      | scenario.carrier_pl_shipping_vinolog | Vinolog | by oid: delivery_carrier_label_postlogistics.postlogistics |         | 1      | Solutions    |
      | scenario.carrier_pl_shipping_pri_sp  | PRI,SP  | by oid: delivery_carrier_label_postlogistics.postlogistics |         | 1      | Parcel       |

  @carrier_postlogistics_options
  Scenario Outline: I setup a postlogistic carrier options
    Given I need a "delivery.carrier.option" with oid: <oid>
    And having:
      | name           | value             |
      | carrier_id     | by oid: <carrier> |
      | tmpl_option_id | by code: <option> |
      | state          | <state>           |

    Examples: carrier options for PRI,SP
      | oid                              | carrier                             | option | state     |
      | scenario.carrier_option_1_pri_sp | scenario.carrier_pl_shipping_pri_sp | PRI,SP | mandatory |

      | scenario.carrier_option_1_a5     | scenario.carrier_pl_shipping_pri_sp | A5     | option    |
      | scenario.carrier_option_1_a6     | scenario.carrier_pl_shipping_pri_sp | A6     | option    |

    Examples: carrier options for Vinolog
      | oid                               | carrier                              | option | state     |
      | scenario.carrier_option_1_vinolog | scenario.carrier_pl_shipping_vinolog | VL     | mandatory |

      | scenario.carrier_option_1_a5      | scenario.carrier_pl_shipping_vinolog | A5     | option    |
      | scenario.carrier_option_1_a6      | scenario.carrier_pl_shipping_vinolog | A6     | option    |
