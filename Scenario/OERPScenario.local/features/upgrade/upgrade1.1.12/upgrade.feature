# -*- coding: utf-8 -*-
@upgrade_from_1.1.11 @qoqa

Feature: upgrade to 1.1.12

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE attribute_attribute
    SET qoqa_id = 'capacity' WHERE field_id IN (
        SELECT id
        FROM ir_model_fields
        WHERE model = 'product.template'
        AND name = 'wine_bottle_id'
    );
    """

    Given I set the version of the instance to "1.1.12"
