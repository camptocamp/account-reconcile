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
@attribute_set @core_setup

Feature: Configure the attribute sets

  @modules
  Scenario: install modules
    Given I install the required modules with dependencies:
        | name                           |
        | product_custom_attributes      |
    Then we select users below:
    | login |
    | admin |
    And we assign to users the groups below
        | base.group_advanced_attribute |

  @template_attributes
  Scenario Outline: Create attributes for product templates
  Given I need a "attribute.attribute" with oid: scenario.attr_<name>
    And I set the attribute model to oid: procurement.model_product_template
    And having:
        | key               | value                               |
        | name              | x_<name>                            |
        | field_description | <descr>                             |
        | attribute_type    | <type>                              |
        | translate         | <translate>                         |
        | required          | <required>                          |

  Examples: Template attributes
      | name       | descr      | type | translate | required |
      | brand      | Brand      | char | True      | False    |
      | highlights | Highlights | text | True      | False    |

  Examples: Template attributes for the wine
      | name         | descr       | type   | translate | required |
      | winemaker    | Winemaker   | char   | False     | True     |
      | appellation  | Appellation | char   | False     | True     |
      | wine_name    | Wine Name   | char   | False     | False    |
      | millesime    | Millésime   | char   | False     | False    |
      | AOC          | AOC         | boolean| False     | False    |
      | wine_region  | Region      | char   | False     | False    |
      | capacity     | Capacity    | float  | False     | False    |
      | wine_color   | Color       | select | False     | True     |
      | wine_type    | Type        | select | False     | True     |

  @country_options
  Scenario: Create the options for the country attribute
  Given I need a "attribute.attribute" with oid: scenario.attr_country
    And I set the attribute model to oid: procurement.model_product_template
    And having:
        | key               | value                               |
        | name              | x_country                           |
        | field_description | Country                             |
        | attribute_type    | select                              |
        | required          | True                                |
        | relation          | res.country                         |
        | relation_model_id | by oid: base.model_res_country      |
    And I generate the attribute options from the model res.country

  @wine_color_options
  Scenario Outline: Create the options for the wine_color attribute
  Given I need a "attribute.option" with oid: scenario.attr_option_wine_color_<oid>
    And having:
        | key          | value                            |
        | name         | <name>                           |
        | attribute_id | by oid: scenario.attr_wine_color |
        | sequence     | <sequence>                       |

  Examples: Options
      | oid   | name  | sequence |
      | red   | Rouge | 0        |
      | white | Blanc | 1        |
      | rose  | Rosé  | 2        |

  @wine_type_options
  Scenario Outline: Create the options for the wine_type attribute
  Given I need a "attribute.option" with oid: scenario.attr_option_wine_type_<oid>
    And having:
        | key          | value                            |
        | name         | <name>                           |
        | attribute_id | by oid: scenario.attr_wine_type  |
        | sequence     | <sequence>                       |

  Examples: Options
      | oid      | name     | sequence |
      | sec      | Sec      | 0        |
      | mousseux | Mousseux | 1        |
      | other    | Autre    | 2        |

  @variant_attributes
  Scenario Outline: Create attributes for product products
  Given I need a "attribute.attribute" with oid: scenario.attr_<name>
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key               | value                               |
        | name              | x_<name>                            |
        | field_description | <descr>                             |
        | attribute_type    | <type>                              |
        | translate         | <translate>                         |

  Examples: Variant attributes
      | name             | descr            | type      | translate |
      | warranty         | Warranty         | char      | True      |
      | dimension_big    | Dimension big    | float     | True      |
      | dimension_medium | Dimension medium | float     | False     |
      | dimension_small  | Dimension small  | float     | False     |
      | variant_weight   | Variant Weight   | float     | False     |
      # warranty will probably change for the RMA

  @general
  Scenario: Create a general attribute set
  Given I need a "attribute.set" with oid: scenario.set_general
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key  | value       |
        | name | Général     |
  Given I need a "attribute.group" with oid: scenario.group_general_main
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key              | value                        |
        | name             | Caractéristiques principales |
        | attribute_set_id | by oid: scenario.set_general |

  @general_groups
  Scenario Outline: Create attribute locations (set + group + attribute)
  Given I need a "attribute.location" with oid: scenario.attr_location_main_<attribute_name>
    And having:
        | key                | value                                  |
        | attribute_group_id | by oid: scenario.group_general_main    |
        | attribute_id       | by oid: scenario.attr_<attribute_name> |
        | sequence           | <sequence>                             |

  Examples: General Main Groups
      | attribute_name   | sequence |
      | brand            | 0        |
      | highlights       | 1        |
      | warranty         | 2        |
      | dimension_big    | 3        |
      | dimension_medium | 4        |
      | dimension_small  | 5        |
      | variant_weight   | 6        |


  @wine
  Scenario: Create an attribute set for wine
  Given I need a "attribute.set" with oid: scenario.set_wine
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key  | value       |
        | name | Du vin!     |
  Given I need a "attribute.group" with oid: scenario.group_wine_main
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key              | value                        |
        | name             | Caractéristiques principales |
        | attribute_set_id | by oid: scenario.set_wine    |
  Given I need a "attribute.group" with oid: scenario.group_wine_wine
    And I set the attribute model to oid: procurement.model_product_product
    And having:
        | key              | value                        |
        | name             | Caractéristiques du vin      |
        | attribute_set_id | by oid: scenario.set_wine    |

  @wine_group_general
  Scenario Outline: Create attribute locations (set + group + attribute)
  Given I need a "attribute.location" with oid: scenario.attr_location_wine_<attribute_name>
    And having:
        | key                | value                                  |
        | attribute_group_id | by oid: scenario.group_wine_main       |
        | attribute_id       | by oid: scenario.attr_<attribute_name> |
        | sequence           | <sequence>                             |

  Examples: Wine Main Group
      | attribute_name   | sequence |
      | brand            | 0        |
      | highlights       | 1        |
      | warranty         | 2        |
      | dimension_big    | 3        |
      | dimension_medium | 4        |
      | dimension_small  | 5        |
      | variant_weight   | 6        |

  @wine_group_wine
  Scenario Outline: Create attribute locations (set + group + attribute)
  Given I need a "attribute.location" with oid: scenario.attr_location_wine_<attribute_name>
    And having:
        | key                | value                                  |
        | attribute_group_id | by oid: scenario.group_wine_wine       |
        | attribute_id       | by oid: scenario.attr_<attribute_name> |
        | sequence           | <sequence>                             |

  Examples: Wine Group
       | attribute_name | sequence |
       | winemaker      | 10       |
       | appellation    | 11       |
       | wine_name      | 12       |
       | AOC            | 13       |
       | country        | 14       |
       | wine_region    | 15       |
       | capacity       | 16       |
       | wine_color     | 17       |
       | wine_type      | 18       |
