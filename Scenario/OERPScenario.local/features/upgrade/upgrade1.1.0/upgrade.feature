# -*- coding: utf-8 -*-
@upgrade_1.1.0 @qoqa

Feature: upgrade to 1.1.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | qoqa_base_data                             |
      | crm_claim_mail                             |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE res_company
    SET claim_sale_order_regexp = '\*\*\* Numéro de commande : (\d+) \*\*\*'
    """

    Given I set the version of the instance to "1.1.0"
