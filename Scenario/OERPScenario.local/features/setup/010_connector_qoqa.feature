# -*- coding: utf-8 -*-
###############################################################################
#
#    OERPScenario, OpenERP Functional Tests
#    Copyright 2009 Camptocamp SA
#
##############################################################################

# Features Generic tags (none for all)
##############################################################################
# Branch      # Module       # Processes     # System
@connector_qoqa @core_setup

Feature: Configure the connector's backend

  @qoqa_backend
  Scenario: Configure the QoQa backend
  Given I find a "qoqa.backend" with oid: connector_qoqa.qoqa_backend_config
    And having:
         | key             | value                      |
         | url             | https://ch.test02.qoqa.com |
         | default_lang_id | by code: fr_FR             |
