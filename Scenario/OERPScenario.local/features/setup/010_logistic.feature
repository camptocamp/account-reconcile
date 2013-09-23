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
@logistic @core_setup

Feature: Setup the logistic for QoQa
  For each company, we need the following locations:
  SAV, Non-réclamé, Stock, Défectueux

