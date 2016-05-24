# -*- coding: utf-8 -*-
@upgrade_from_1.1.13 @qoqa

Feature: upgrade to 1.1.14

  Scenario: upgrade application version
    Given I update the module list
    Given I execute the SQL commands
    """
    -- Deactivate cron for connector_qoqa
    UPDATE ir_cron
    SET active=False
    WHERE name ilike 'QoQa - Import%';
    -- Rename base_login_date_improvement as base_concurrency
    UPDATE ir_model_data
    SET module='base_concurrency'
    WHERE module='base_login_date_improvement'
    AND model like 'ir.model%';
    UPDATE ir_module_module set state='to remove' where name='base_login_date_improvement';
    """
    Given I uninstall the following modules:
      | name                             |
      | base_login_date_improvement      |
    Given I install the required modules with dependencies:
      | name                             |
      | connector_qoqa                   |
      | base_concurrency                 |
      | specific_fct                     |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    -- Insert current values in qoqa_backend_timestamp
    INSERT INTO qoqa_backend_timestamp
    (backend_id, from_date_field, import_start_time)
    VALUES (
        1,
        'import_product_template_from_date',
        (SELECT import_product_template_from_date
         FROM qoqa_backend
         WHERE id = 1)
    );
    INSERT INTO qoqa_backend_timestamp
    (backend_id, from_date_field, import_start_time)
    VALUES (
        1,
        'import_product_product_from_date',
        (SELECT import_product_product_from_date
         FROM qoqa_backend
         WHERE id = 1)
    );
    INSERT INTO qoqa_backend_timestamp
    (backend_id, from_date_field, import_start_time)
    VALUES (
        1,
        'import_res_partner_from_date',
        (SELECT import_res_partner_from_date
         FROM qoqa_backend
         WHERE id = 1)
    );
    INSERT INTO qoqa_backend_timestamp
    (backend_id, from_date_field, import_start_time)
    VALUES (
        1,
        'import_address_from_date',
        (SELECT import_address_from_date
         FROM qoqa_backend
         WHERE id = 1)
    );
    INSERT INTO qoqa_backend_timestamp
    (backend_id, from_date_field, import_start_time)
    VALUES (
        1,
        'import_sale_order_from_date',
        (SELECT import_sale_order_from_date
         FROM qoqa_backend
         WHERE id = 1)
    );
    INSERT INTO qoqa_backend_timestamp
    (backend_id, from_date_field, import_start_time)
    VALUES (
        1,
        'import_accounting_issuance_from_date',
        (SELECT import_accounting_issuance_from_date
         FROM qoqa_backend
         WHERE id = 1)
    );
    INSERT INTO qoqa_backend_timestamp
    (backend_id, from_date_field, import_start_time)
    VALUES (
        1,
        'import_offer_from_date',
        (SELECT import_offer_from_date
         FROM qoqa_backend
         WHERE id = 1)
    );
    INSERT INTO qoqa_backend_timestamp
    (backend_id, from_date_field, import_start_time)
    VALUES (
        1,
        'import_offer_position_from_date',
        (SELECT import_offer_position_from_date
         FROM qoqa_backend
         WHERE id = 1)
    );


    -- Re-activate crons (except product images)
    UPDATE ir_cron
    SET active=True
    WHERE name ilike 'QoQa - Import%'
    AND name != 'QoQa - Import Product Images';
    """

    Given I re-export to QoQa the wine products
    Given I set the version of the instance to "1.1.14"
