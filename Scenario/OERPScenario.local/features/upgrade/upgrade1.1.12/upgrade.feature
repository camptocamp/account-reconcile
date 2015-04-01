# -*- coding: utf-8 -*-
@upgrade_from_1.1.11 @qoqa

Feature: upgrade to 1.1.12

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | crm_claim_mail                             |
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

    UPDATE ir_act_server
    SET code = 'template_id = object.confirmation_email_template and object.confirmation_email_template.id or self.pool[''ir.model.data''].get_object_reference(cr, uid, ''crm_claim_mail'', ''email_template_rma_received'')[1]
self.pool[''email.template''].send_mail(cr, uid, template_id, object.id)'
    WHERE name = 'Send an email when a claim is created';
    """

    Given I set the version of the instance to "1.1.12"
