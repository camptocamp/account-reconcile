# -*- coding: utf-8 -*-
@upgrade_to_1.6 @qoqa

Feature: upgrade to 1.6

  Scenario: upgrade application version

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                    |
      | connector_qoqa          |
      | crm_claim_mail          |
      | email_template_dateutil |
      | qoqa_claim              |
    Then my modules should have been installed and models reloaded

  Scenario: add claim categories to company
    Given I need a "res.company" with oid: scenario.qoqa_ch
    And having:
    | key                                | value                                           |
    | unclaimed_initial_categ_id         | by name: Non-réclamé - 1er rappel               |
    | unclaimed_first_reminder_categ_id  | by name: Non-réclamé - 2e rappel                |
    | unclaimed_second_reminder_categ_id | by name: Non-réclamé - 3. Dernier rappel lettre |

  Scenario: add user to sales team and don't notify on change
    Given I need a "crm.case.section" with oid: scenario.section_sale_team_livr
    And having:
    | key     | value           |
    | user_id | by name: Sandra |
    | notify  | false           |

  Scenario: add normal prices on delivery carriers
    Given I need a "delivery.carrier" with name: PostPac PRI+SI Std <1kg
    And having:
    | key          | value |
    | normal_price | 7.00  |

    Given I need a "delivery.carrier" with oid: scenario.carrier_postpac_prisi_std
    And having:
    | key          | value |
    | normal_price | 9.00  |

    Given I need a "delivery.carrier" with oid: scenario.carrier_vinolog
    And having:
    | key          | value |
    | normal_price | 12.00 |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.6"
