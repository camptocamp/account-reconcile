# -*- coding: utf-8 -*-
@migration @9.0 @qoqa

Feature: Parameter the new database
  In order to have a coherent installation
  I've automated the manual steps.

  @clean
  Scenario: when we receive the database from the migration service, addons are 'to upgrade', set them to uninstalled.
    Given I execute the SQL commands
    """
    UPDATE ir_module_module set state = 'uninstalled' where state IN ('to install', 'to upgrade');
    """

  @clean
  Scenario: remove the 'retry missing' flag on cron to avoid having them running again and again
    Given I execute the SQL commands
    """
    UPDATE ir_cron SET doall = false WHERE doall = true;
    """

  @clean
  Scenario: clean the stuff of old modules
    Given I delete all the ir.ui.view records created by uninstalled modules
    And I delete all the assembled.report records created by uninstalled modules
    And I delete all the ir.actions.act_window records created by uninstalled modules
    And I delete all the ir.actions.act_window.view records created by uninstalled modules
    And I delete all the ir.actions.client records created by uninstalled modules
    And I delete all the ir.actions.report.xml records created by uninstalled modules
    And I delete all the ir.actions.server records created by uninstalled modules
    And I delete all the ir.cron records created by uninstalled modules
    And I delete all the ir.rule records created by uninstalled modules
    And I delete all the ir.ui.menu records created by uninstalled modules
    And I delete all the ir.values records created by uninstalled modules
    And I delete the broken ir.values

  @move_wine_xmlid
  Scenario: Move wine_ch_report xmlids to qoqa_product
    Given I execute the SQL commands
    """
    UPDATE ir_model_data SET module = 'qoqa_product'
    WHERE module = 'wine_ch_report'
    AND model in ('wine.class', 'wine.bottle')
    """

  @fix_claim_line_origin
  Scenario: a required field 'claim_origin' has been added and is empty
    Given I execute the SQL commands
    """
    ALTER TABLE claim_line ADD COLUMN claim_origin varchar
    """
    Given I execute the SQL commands
    """
    UPDATE claim_line SET claim_origin = claim_origine
    WHERE claim_origine IS NOT NULL AND claim_origin IS NULL
    """

  @fix_claim_rma_update
  Scenario: lines in a wizard make the upgrade fail
    Given I execute the SQL commands
    """
    DELETE FROM claim_make_picking_wizard
    """
    Given I execute the SQL commands
    """
    UPDATE ir_model_data SET name = 'team_after_sales_service'
    WHERE name = 'section_after_sales_service' AND model = 'crm.team';
    """

  @update_module_list
  Scenario: Update module list before updating to avoid draging old dependancies
  Given I update the module list

  @modules
  Scenario: install modules
    Given I install the required modules with dependencies:
        | name                                            |
        #---- Base ---------------------------------------#
        | account                                         |
        | base_import                                     |
        | document                                        |
        | stock                                           |
        | sale                                            |
        | l10n_ch                                         |
        | l10n_fr                                         |
        | l10n_multilang                                  |
        # old official modules
        #| multi_company                                   |
        #---- OCA/account-financial-reporting ------------#
        #| account_export_csv                              |
        #| account_financial_report_webkit [DEPRECATED]    |
        #---- OCA/account-financial-tools ----------------#
        #| account_constraints                             |
        #| account_default_draft_move                      |
        | account_permanent_lock_move                     |
        #| account_reversal                                |
        #| currency_rate_update                            |
        #---- OCA/account-fiscal-rule --------------------#
        #| account_fiscal_position_rule                    |
        #| account_fiscal_position_rule_sale               |
        #---- OCA/account-invoice-reporting --------------#
        #| invoice_webkit [DEPRECATED]                     |
        #---- OCA/bank-payment ---------------------------#
        | account_payment_mode                            |
        | account_payment_sale                            |
        #---- OCA/bank-statement-reconcile ---------------#
        | account_mass_reconcile                          |
        | account_move_base_import                        |
        | account_move_transactionid_import               |
        | base_transaction_id                             |
        #| invoicing_voucher_killer [DEPRECATED]           |
        #| statement_voucher_killer [DEPRECATED]           |
        #---- OCA/carrier-delivery -----------------------#
        | base_delivery_carrier_label                     |
        | delivery_carrier_label_postlogistics            |
        | delivery_carrier_label_postlogistics_shop_logo  |
        #---- OCA/connector-ecommerce --------------------#
        #| connector_ecommerce                             |
        #---- OCA/crm ------------------------------------#
        | crm_claim_merge                                 |
        #---- OCA/margin-analysis ------------------------#
        #| product_cost_incl_bom                           |
        #| product_cost_incl_bom_price_history             |
        #| product_get_cost_field                          |
        #| product_historical_margin                       |
        #| product_price_history                           |
        #| product_standard_margin                         |
        #| product_stock_cost_field_report                 |
        #---- OCA/l10n-france ----------------------------#
        #| l10n_fr_rib                                     |
        #---- OCA/l10n-switzerland -----------------------#
        | l10n_ch_bank                                    |
        | l10n_ch_base_bank                               |
        #| l10n_ch_dta                                     |
        | l10n_ch_payment_slip                            |
        | l10n_ch_zip                                     |
        #---- OCA/product-attributes ---------------------#
        | product_brand                                   |
        #---- OCA/purchase-workflow ----------------------#
        | purchase_discount                               |
        #| purchase_landed_costs                           |
        #---- OCA/rma ------------------------------------#
        | crm_claim_rma                                   |
        | crm_rma_stock_location                          |
        #---- OCA/sale-reporting -------------------------#
        #| sale_order_webkit                               |
        #| sale_jit_on_services                            |
        #---- OCA/sale-workflow  -------------------------#
        | sale_automatic_workflow                         |
        | sale_automatic_workflow_payment_mode            |
        #---- OCA/server-tools ---------------------------#
        | mail_cleanup                                    |
        | mail_environment                                |
        | base_technical_features                         |
        #---- OCA/stock-logistics-warehouse --------------#
        | stock_orderpoint_generator                      |
        #---- OCA/stock-logistics-workflow ---------------#
        #| picking_dispatch                                |
        #---- OCA/web ------------------------------------#
        | web_send_message_popup                          |
        #| web_translate_dialog                            |
        #---- QoQa specifics -----------------------------#
        #| base_stock_picking_pack_split                   |
        | account_s3_move_import                          |
        #| connector_qoqa                                  |
        #| crm_claim_mail                                  |
        | crm_rma_by_shop                                  |
        #| delivery_carrier_label_swiss_pp                 |
        #| delivery_carrier_url                            |
        #| ecotax                                          |
        | picking_dispatch_delay_done                     |
        #| picking_dispatch_group                          |
        #| purchase_variant_fast_entry                     |
        #| qoqa_base_data                                  |
        #| qoqa_claim                                      |
        #| qoqa_label_dispatch_pack_split                  |
        #| qoqa_offer                                      |
        #| qoqa_offer_historical_margin                    |
        | qoqa_product                          |
        | qoqa_record_archiver                            |
        #| server_env_connector_qoqa                       |
        #| specific_fct                                    |
        #| specific_report                                 |
        | speedy_views                                    |
        #| web_custom                                      |
        | web_environment |
        #| wine_ch_report                                  |
    Then my modules should have been installed and models reloaded

  @lang
  Scenario: install lang
   Given I install the following language :
      | lang  |
      | fr_FR |
      | de_DE |
   Then the language should be available
    Given I find a "res.lang" with code: en_US
    And having:
         | key      | value  |
         | grouping | [3, 0] |
    Given I find a "res.lang" with code: fr_FR
    And having:
         | key      | value    |
         | grouping | [3, 0]   |
         | name     | Français |
    Given I find a "res.lang" with code: de_DE
    And having:
         | key      | value   |
         | grouping | [3, 0]  |
         | name     | Deutsch |

  @currencies
  Scenario: Activate currencies
    Given  I execute the SQL commands
    """
    UPDATE res_currency SET active = TRUE
      WHERE name IN ('EUR', 'CHF', 'USD')
    """

  @company
  Scenario: Configure main partner and company
  Given I find a "res.company" with oid: base.main_company
    And having:
         | key                       | value        |
         | name                      | QoQa Holding |
         | currency_id               | by name: CHF |
    Given the company has the "images/logo_qoqa_ch.png" logo

  @product_attribute_variants
  Scenario: migrate product attributes from the custom wizard to the odoo core variant attributes
    Given I migrate the product attribute variants

  @product_brand
  Scenario: migrate char field 'brand' to product_brand addon
    Given I execute the SQL commands
    """
    INSERT INTO product_brand (name)
    SELECT distinct brand FROM product_template t
    WHERE NOT EXISTS (SELECT id FROM product_brand WHERE name = t.brand)
    AND brand IS NOT NULL
    """
    Given I execute the SQL commands
    """
    UPDATE product_template
    SET product_brand_id = (SELECT id FROM product_brand WHERE name = product_template.brand)
    WHERE brand IS NOT NULL and product_brand_id IS NULL
    """

  @product_attributes
  Scenario: migrate product dynamic attributes to regular fields
    Given I execute the SQL commands
    """
    UPDATE product_template SET is_wine = True
    WHERE attribute_set_id = (
      SELECT id FROM attribute_set
      WHERE id = (
        SELECT res_id FROM ir_model_data
        WHERE model = 'attribute.set'
        AND name = 'set_wine'
      )
    )
    """
    Given I execute the SQL commands
    """
    UPDATE product_template SET is_liquor = True
    WHERE attribute_set_id = (
      SELECT id FROM attribute_set
      WHERE id = (
        SELECT res_id FROM ir_model_data
        WHERE model = 'attribute.set'
        AND name = 'set_liquor'
      )
    )
    """
    Given I execute the SQL commands
    """
    INSERT INTO wine_winemaker (name, create_date, write_date, create_uid, write_uid)
    SELECT TRIM(o.name),
           MIN(o.create_date),
           MIN(o.write_date),
           MIN(o.create_uid),
           MIN(o.write_uid)
      FROM product_template t
      INNER JOIN attribute_option o
      ON o.id = t.x_winemaker
      AND o.attribute_id = (
        SELECT id
        FROM attribute_attribute
        WHERE field_id = (
          SELECT id FROM ir_model_fields
          WHERE name = 'x_winemaker' AND model = 'product.template'
        )
      )
      WHERE t.x_winemaker IS NOT NULL
      AND NOT EXISTS (SELECT id FROM wine_winemaker WHERE name = TRIM(o.name))
      GROUP BY TRIM(o.name)
    """
    Given I execute the SQL commands
    """
    UPDATE product_template t
    SET winemaker_id = (
      SELECT w.id
      FROM wine_winemaker w
      INNER JOIN attribute_option o
      ON TRIM(o.name) = w.name
      INNER JOIN attribute_attribute a
      ON a.id = o.attribute_id
      INNER JOIN ir_model_fields f
      ON f.id = a.field_id
      AND f.name = 'x_winemaker' AND f.model = 'product.template'
      WHERE o.id = t.x_winemaker
    )
    WHERE x_winemaker IS NOT NULL AND winemaker_id IS NULL;
    """
    Given I execute the SQL commands
    """
    INSERT INTO wine_type (name, create_date, write_date, create_uid, write_uid)
    SELECT TRIM(o.name),
           MIN(o.create_date),
           MIN(o.write_date),
           MIN(o.create_uid),
           MIN(o.write_uid)
      FROM product_template t
      INNER JOIN attribute_option o
      ON o.id = t.x_wine_type
      AND o.attribute_id = (
        SELECT id
        FROM attribute_attribute
        WHERE field_id = (
          SELECT id FROM ir_model_fields
          WHERE name = 'x_wine_type' AND model = 'product.template'
        )
      )
      WHERE t.x_wine_type IS NOT NULL
      AND NOT EXISTS (SELECT id FROM wine_type WHERE name = TRIM(o.name))
      GROUP BY TRIM(o.name)
    """
    Given I execute the SQL commands
    """
    UPDATE product_template t
    SET wine_type_id = (
      SELECT w.id
      FROM wine_type w
      INNER JOIN attribute_option o
      ON TRIM(o.name) = w.name
      INNER JOIN attribute_attribute a
      ON a.id = o.attribute_id
      INNER JOIN ir_model_fields f
      ON f.id = a.field_id
      AND f.name = 'x_wine_type' AND f.model = 'product.template'
      WHERE o.id = t.x_wine_type
    )
    WHERE x_wine_type IS NOT NULL AND wine_type_id IS NULL
    """
    Given I execute the SQL commands
    """
    UPDATE product_template SET appellation = x_appellation WHERE x_appellation IS NOT NULL
    """
    Given I execute the SQL commands
    """
    UPDATE product_template SET millesime = x_millesime WHERE x_millesime IS NOT NULL
    """
    Given I execute the SQL commands
    """
    UPDATE product_template SET country_id = x_country_id WHERE x_country_id IS NOT NULL
    """
    Given I execute the SQL commands
    """
    UPDATE product_template SET ageing = x_ageing WHERE x_ageing IS NOT NULL
    """
    Given I execute the SQL commands
    """
    UPDATE product_template SET abv = x_abv WHERE x_abv IS NOT NULL
    """
    Given I execute the SQL commands
    """
    UPDATE product_template SET wine_short_name = x_wine_short_name WHERE x_wine_short_name IS NOT NULL
    """
    Given I execute the SQL commands
    """
    UPDATE product_template SET wine_region = x_wine_region WHERE x_wine_region IS NOT NULL
    """

  @sale_shop
  Scenario: migrate sale.shop to qoqa.shop
    # TODO: add fields that do not exist yet
    Given I execute the SQL commands
    """
    UPDATE qoqa_shop q
    SET name = s.name,
        kanban_image = s.kanban_image,
        company_id = s.company_id
    -- TODO:
    -- postlogistics_logo, swiss_pp_logo, mail_signature_template
    FROM sale_shop s
    WHERE s.id = q.openerp_id
    """
    Given I execute the SQL commands
    """
    UPDATE crm_claim c
    SET qoqa_shop_id = q.id
    FROM qoqa_shop q
    WHERE q.openerp_id = c.shop_id
    AND shop_id IS NOT NULL AND qoqa_shop_id IS NULL
    """
    Given I execute the SQL commands
    """
    UPDATE sale_order c
    SET qoqa_shop_id = q.id
    FROM qoqa_shop q
    WHERE q.openerp_id = c.shop_id
    AND shop_id IS NOT NULL AND qoqa_shop_id IS NULL
    """
