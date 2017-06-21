# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.uninstaller import uninstall


@anthem.log
def main(ctx):
    # we will uninstalled modules
    uninstall(ctx, ['website_crm_claim', 'survey_crm',
                    'hr_appraisal', 'website_mail',
                    'survey', 'website_theme_install',
                    'website_enterprise', 'website'])
