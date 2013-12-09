# -*- coding: utf-8 -*-

@currency_rate_update @setup
Feature: Parameter pricelists
  In order to configure module currency_rate_update
  I set the parameters in company settings
  Scenario: setup currency_rate_update
    Given I need a "currency.rate.update.service" with oid: scen.currency_up_service_admin_ch
    And having:
         | name               | value                |
         | service            | Admin_ch_getter      |
         | currency_to_update | add all by name: EUR |
         | currency_to_update | add all by name: USD |
    Given I find a "res.company" with oid: base.main_company
    And having:
         | name             | value                                |
         | auto_currency_up | True                                 |
         | services_to_use  | by oid: scen.currency_up_service_ecb |
         | interval_type    | days                                 |
