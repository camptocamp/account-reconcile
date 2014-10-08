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
    SET url_template = 'https://www.mypostbusiness.ch/EasyTrack/submitParcelData.do?formattedParcelCodes=%(tracking_number)s&lang=%(lang)s'
    WHERE type = 'postlogistics'
    """
    
    Given I execute the SQL commands
    """
    UPDATE qoqa_backend
    SET import_product_product_from_date = '2014-10-01 00:00:00'
    WHERE id = 1
    """

    Given I set the version of the instance to "1.1.2"
