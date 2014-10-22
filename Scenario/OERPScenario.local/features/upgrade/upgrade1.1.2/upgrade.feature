# -*- coding: utf-8 -*-
@upgrade_1.1.2 @qoqa

Feature: upgrade to 1.1.2

  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | delivery_carrier_url                       |
      | qoqa_offer                                 |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE delivery_carrier
    SET url_template = 'https://www.post.ch/EasyTrack/submitParcelData.do?domain=www.post.ch&reference=%%252fswisspost-tracking&formattedParcelCodes=%(tracking_number)s&p_language=%(lang)s&DCSext.wt_shortcut=swisspost-tracking&WT.mc_id=shortcut_swisspost-tracking'
    WHERE type = 'postlogistics'
    """

    Given I set the version of the instance to "1.1.2"
