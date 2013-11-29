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
# Create an alias per alias in gmail to affect the right team
  Scenario: I configure postlogistics authentification
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
      | name                           | value                       |
      | postlogistics_username         | TU_9272_06                  |
      | postlogistics_password         | x1KsSvyY6X                  |
      | postlogistics_license_less_1kg | 60035471                    |
      | postlogistics_license_more_1kg | 60035471                    |
      | postlogistics_license_vinolog  | 60035471                    |
      | postlogistics_office           | 1030 Bussigny-près-Lausanne |

  @postlogistics_options_update
  Scenario: I update postlogistics services (It will take 1 minute)
    Given I am configuring the company with ref "scenario.qoqa_ch"
    And I update postlogistics services

  @carrier_postlogistics_groups
  Scenario Outline: I setup a postlogistic carrier
    Given I need a "delivery.carrier" with oid: <oid>
    And having:
      | key                            | value                   |
      | type                           | postlogistics           |
      | postlogistics_service_group_id | by name: <service_name> |

    Examples:
      | oid                              | service_name |
      | scenario.carrier_pl_advanced     | Parcel       |
      | scenario.carrier_pl_alcool       | Solutions    |
      | scenario.carrier_pl_basic        | Parcel       |
      | scenario.carrier_pl_big          | Parcel       |
      | scenario.carrier_pl_big_spec49   | Parcel       |
      | scenario.carrier_pl_large        | Parcel       |
      | scenario.carrier_pl_light_weight | Parcel       |
      | scenario.carrier_pl_light699     | Parcel       |
      | scenario.carrier_pl_medium       | Parcel       |
      | scenario.carrier_pl_vino_basic   | Solutions    |
      | scenario.carrier_pl_vino_1_12    | Solutions    |
      | scenario.carrier_pl_vino3        | Solutions    |

  @carrier_postlogistics_options
  Scenario Outline: I setup a postlogistic carrier options
    Given I need a "delivery.carrier.option" with oid: <oid>
    And having:
      | name           | value             |
      | carrier_id     | by oid: <carrier> |
      | tmpl_option_id | by code: <option> |
      | state          | <state>           |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_1_basic| scenario.carrier_pl_advanced | PRI,SP | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_2_basic| scenario.carrier_pl_alcool | VL | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_3_basic| scenario.carrier_pl_basic | PRI,SP | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_4_basic| scenario.carrier_pl_big| PRI,SP | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_5_basic| scenario.carrier_pl_big_spec49 | PRI,SP | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_6_basic| scenario.carrier_pl_large | PRI,SP | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_7_basic| scenario.carrier_pl_light_weight | PRI | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_8_basic| scenario.carrier_pl_light699 | PRI | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_9_basic| scenario.carrier_pl_medium | PRI | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_10_basic| scenario.carrier_pl_vino_basic | VL | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      |scenario.carrier_option_11_basic| scenario.carrier_pl_vino_1_12 | VL | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |

    Examples:
      |oid| carrier | option | state |
      | scenario.carrier_option_12_basic | scenario.carrier_pl_vino3 | VL | mandatory |

      |scenario.carrier_option_1_pdf| scenario.carrier_pl_advanced | PDF | option |
      |scenario.carrier_option_1_a5| scenario.carrier_pl_advanced | A5 | option |
      |scenario.carrier_option_1_a6| scenario.carrier_pl_advanced | A6 | option |
      |scenario.carrier_option_1_a7| scenario.carrier_pl_advanced | A7 | option |
      |scenario.carrier_option_1_300pp| scenario.carrier_pl_advanced | 300 | option |
