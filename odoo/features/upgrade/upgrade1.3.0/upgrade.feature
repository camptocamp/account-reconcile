# -*- coding: utf-8 -*-
@upgrade_from_1.2 @qoqa

Feature: upgrade to 1.3.0

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I execute the SQL commands
    """
    DROP INDEX IF EXISTS res_partner_display_name_index_tmp;
    """
    Given I execute the SQL commands
    """
    DROP INDEX IF EXISTS account_move_line_journal_id_period_id_index;
    CREATE INDEX account_move_line_journal_id_period_id_index
    ON account_move_line (journal_id, period_id, state, create_uid, id DESC);
    """

    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                                   |
      | l10n_ch                                                |
      | l10n_ch_bank                                           |
      | l10n_ch_base_bank                                      |
      | l10n_ch_dta                                            |
      | l10n_ch_dta_base_transaction_id                        |
      | l10n_ch_payment_slip                                   |
      | l10n_ch_payment_slip_account_statement_base_completion |
      | l10n_ch_payment_slip_base_transaction_id               |
      | l10n_ch_sepa                                           |
      | l10n_ch_zip                                            |
      | mail_cleanup                                           |
      | specific_fct                                           |
      | record_archiver                                        |
      | qoqa_record_archiver                                   |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE crm_claim
    SET partner_id = res_partner.parent_id
    FROM res_partner
    WHERE crm_claim.partner_id = res_partner.id
    AND res_partner.parent_id IS NOT NULL;
    """

  Scenario: update warranty for specific categories
    Given I execute the SQL commands
    """
    UPDATE product_category
    SET warranty = 0
    WHERE id IN (39, 40, 41, 42, 43, 179, 180, 181, 182, 183, 196, 199, 201, 202);
    """

  Scenario Outline: setup cron to archive old records
    Given I need a "record.lifespan" with oid: scenario.lifespan_<oid>
    And having:
      | name       | value                    |
      | model_id   | by model: <model>        |
      | months     | <months>                 |
  Examples:
      | oid              | model            | months |
      | sale_order       | sale.order       | 24     |
      | qoqa_offer       | qoqa.offer       | 6      |
      | stock_picking    | stock.picking    | 3      |
      | picking_dispatch | picking.dispatch | 3      |
      | purchase_order   | purchase.order   | 6      |
      | account_invoice  | account.invoice  | 24     |
      | crm_claim        | crm.claim        | 24     |

  Scenario: upgrade application version
    Given I set the version of the instance to "1.3.0"
