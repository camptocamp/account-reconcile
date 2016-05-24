# -*- coding: utf-8 -*-
@upgrade_from_1.1.12 @qoqa

Feature: upgrade to 1.1.13

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | connector                                  |
      | crm_claim_mail                             |
      | base_login_date_improvement                |
      | specific_fct                               |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    -- Update attribute to sync with QoQa back-office.
    UPDATE attribute_attribute
    SET qoqa_id = 'capacity' WHERE field_id IN (
        SELECT id
        FROM ir_model_fields
        WHERE model = 'product.template'
        AND name = 'wine_bottle_id'
    );

    -- Update server action to use new optional template per alias
    UPDATE ir_act_server
    SET code = 'template_id = object.confirmation_email_template and object.confirmation_email_template.id or self.pool[''ir.model.data''].get_object_reference(cr, uid, ''crm_claim_mail'', ''email_template_rma_received'')[1]
    self.pool[''email.template''].send_mail(cr, uid, template_id, object.id)'
    WHERE name = 'Send an email when a claim is created';

    -- Correct existing reconciliations done automatically but marked as manual
    UPDATE account_move_reconcile
    SET type = 'auto'
    WHERE type = 'manual'
    AND create_uid IN (1,6,7);

    -- Fix cases where a french invoice had swiss accounts (issues with automatic workflow)
    UPDATE account_invoice SET account_id = 1906 WHERE account_id = 1460 and company_id = 4;
    UPDATE account_invoice_line SET account_id = 2373 WHERE account_id = 576 and company_id = 4;
    UPDATE account_invoice_line SET account_id = 2381 WHERE account_id = 580 and company_id = 4;
    UPDATE account_invoice_line SET account_id = 2544 WHERE account_id = 1180 and company_id = 4;

    -- Set entries on opening periods in 01/2015 (FR or CH)
    UPDATE account_invoice SET period_id = 69 where period_id = 68;
    UPDATE account_invoice SET period_id = 55 where period_id = 54;
    UPDATE account_move SET period_id = 69 where period_id = 68;
    UPDATE account_move SET period_id = 55 where period_id = 54;
    UPDATE account_move_line SET period_id = 69 where period_id = 68;
    UPDATE account_move_line SET period_id = 55 where period_id = 54;
    """

    Given I re-export to QoQa the wine products
    Given I set the version of the instance to "1.1.13"
