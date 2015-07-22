# -*- coding: utf-8 -*-
@upgrade_from_1.2 @qoqa

Feature: upgrade to 1.3.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                             |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE crm_claim
    SET partner_id = res_partner.parent_id
    FROM res_partner
    WHERE crm_claim.partner_id = res_partner.id
    AND res_partner.parent_id IS NOT NULL;
    """

    Given I set the version of the instance to "1.3.0"
