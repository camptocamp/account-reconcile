# -*- coding: utf-8 -*-
@upgrade_from_1.0.0 @qoqa

Feature: upgrade to 1.0.1

  Scenario: upgrade
    Given I back up the database to "/srv/openerp/before_upgrade_backups"
    Given I install the required modules with dependencies:
      | name                       |
      | connector_qoqa             |
      | account_compute_tax_amount |
    Then my modules should have been installed and models reloaded

  @voucher @qoqa_backend
  Scenario: Configure the vouchers issuance on QoQa backend
    Given user "admin_ch" log in with password "admin_ch"
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I find a "qoqa.backend" with oid: connector_qoqa.qoqa_backend_config
    And having:
      | key                         | value                             |
      | property_voucher_journal_id | by name: Règlement par Bon Cadeau |
    Given user "admin_fr" log in with password "admin_fr"
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I find a "qoqa.backend" with oid: connector_qoqa.qoqa_backend_config
    And having:
      | key                         | value                             |
      | property_voucher_journal_id | by name: Règlement par Bon Cadeau |
    Then login with the admin user

  @translations
  Scenario: Fix some translations
    Given I execute the SQL commands
    """
    UPDATE account_journal SET name = 'Bons Remboursement' WHERE id in (47, 53);
    UPDATE ir_translation SET value = 'Bons Remboursement' WHERE value like 'Bon%Remboursement%';
    UPDATE account_journal SET name = 'Bons de réduction' WHERE id = 46;
    UPDATE ir_translation SET value = 'Bons de réduction' WHERE value like 'Bon de réduction';
    UPDATE account_journal SET name = 'Bons Rabais' WHERE id = 52;
    UPDATE ir_translation SET value = 'Bons Rabais' WHERE value like 'Bon Rabais';
    UPDATE account_account SET name = 'Bons Remboursement' WHERE id in (2545);
    UPDATE account_account SET name = 'Bons de réduction' WHERE id in (2543);
    UPDATE account_account SET name = 'Bons Marketing' WHERE id in (2544);
    UPDATE account_account SET name = 'Différences d''arrondis' WHERE id in (2546);
    DELETE FROM ir_translation WHERE res_id = 2546 and lang = 'de_DE' and name = 'account.account,name';
    """

  @promo @qoqa_backend
  Scenario Outline: Configure the promos issuance
    Given user "<user>" log in with password "<user>"
    Given I am configuring the company with ref "<company>"
    Given I find a "qoqa.promo.type" with oid: <promo_type_oid>
    And having:
      | key                 | value                   |
      | property_journal_id | by name: <journal_name> |
    Then login with the admin user

    Examples: CH
      | user     | company          | promo_type_oid                             | journal_name       |
      | admin_ch | scenario.qoqa_ch | connector_qoqa.promo_type_customer_service | Bons Rabais        |
      | admin_ch | scenario.qoqa_ch | connector_qoqa.promo_type_refund_coupon    | Bons Remboursement |

    Examples: FR
      | user     | company          | promo_type_oid                             | journal_name       |
      | admin_fr | scenario.qoqa_fr | connector_qoqa.promo_type_customer_service | Bons de réduction  |
      | admin_fr | scenario.qoqa_fr | connector_qoqa.promo_type_refund_coupon    | Bons Remboursement |

  @product @taxes @default
  Scenario: I set the default values for the taxes on the products
    Given I load the data file "setup/ir.values.yml"
    # OpenERP sets a value by default a key which prevent the default
    # value to be applied! It absolutely needs a NULL, which we can't
    # set with the ORM...
    And I execute the SQL commands
    """
    UPDATE ir_values SET key2 = NULL WHERE id IN (
        SELECT res_id FROM ir_model_data
        WHERE module = 'scenario'
        AND name IN ('ir_values_product_taxes_ch',
                     'ir_values_product_taxes_fr',
                     'ir_values_product_taxes_holding',
                     'ir_values_product_supplier_taxes_ch',
                     'ir_values_product_supplier_taxes_fr',
                     'ir_values_product_supplier_taxes_holding',
                     'ir_values_template_taxes_ch',
                     'ir_values_template_taxes_fr',
                     'ir_values_template_taxes_holding',
                     'ir_values_template_supplier_taxes_ch',
                     'ir_values_template_supplier_taxes_fr',
                     'ir_values_template_supplier_taxes_holding')
    )
    """

  @taxes @ch
  Scenario Outline: rename taxes with "TTC"
    Given I am configuring the company with ref "scenario.qoqa_ch"
    Given I find a "account.tax" with name: <name>
    And having:
      | key         | value          |
      | description | <new_tax_code> |

    Examples: currencies
      | name                | new_tax_code |
      | TVA due a 2.5% (TR) | 2.5% TTC     |
      | TVA due a 3.8% (TS) | 3.8% TTC     |
      | TVA due a 8.0% (TN) | 8.0% TTC     |
      | TVA 0% exclue       | 0% excl. TTC |
      | TVA due a 7.6% (TN) | 7.6% TTC     |
      | TVA due a 3.6% (TN) | 3.6% TTC     |
      | TVA due a 2.4% (TN) | 2.4% TTC     |

  @taxes @fr
  Scenario Outline: rename taxes with "TTC"
    Given I am configuring the company with ref "scenario.qoqa_fr"
    Given I find a "account.tax" with name: <name>
    And having:
      | key         | value          |
      | description | <new_tax_code> |

    Examples: currencies
      | name                        | new_tax_code |
      | TVA collectée (vente) 20,0% | 20.0 TTC     |
      | TVA collectée (vente) 7,0%  | 7.0 TTC      |
      | TVA collectée (vente) 10,0% | 10.0 TTC     |
      | TVA collectée (vente) 8,5%  | 8.5 TTC      |
      | TVA collectée (vente) 2,1%  | 2.1 TTC      |
      | TVA collectée (vente) 5,5%  | 5.5 TTC      |
      | TVA collectée (vente) 5,0%  | 5.0 TTC      |
      | TVA collectée (vente) 19,6% | 19.6 TTC     |

  Scenario: update application version
    Given I set the version of the instance to "1.0.1"
