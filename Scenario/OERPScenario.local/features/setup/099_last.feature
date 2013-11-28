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
@last  @setup

Feature: Configure things which must be done after all the other things... update or fix values

  @product @taxes
  Scenario: fix product taxes
    Given I set the taxes on all products
