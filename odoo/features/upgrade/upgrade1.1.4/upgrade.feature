# -*- coding: utf-8 -*-
@upgrade_1.1.4 @qoqa

Feature: upgrade to 1.1.4

  # Before scenario: ./bin/start_openerp -u qoqa_offer, crm_claim_mail
  Scenario: upgrade application version
    Given I back up the database to "/var/tmp/openerp/before_upgrade_backups"
    Given I update the module list
    Given I install the required modules with dependencies:
      | name                                       |
      | qoqa_offer                                 |
      | connector_qoqa                             |
      | web_environment                            |
      | specific_fct                               |
      | crm_claim_mail                             |
      | specific_fct                               |
    Then my modules should have been installed and models reloaded

    Given I execute the SQL commands
    """
    UPDATE qoqa_backend
    SET import_product_product_from_date = '2014-10-01 00:00:00'
    WHERE id = 1
    """

    # Remove shops mail signature if exist
     Given I execute the SQL commands
    """
    DELETE FROM ir_translation
    WHERE name = 'sale.shop,mail_signature_template' AND type = 'model';
    """
    # Remove companies mail signature if exist
    Given I execute the SQL commands
    """
    DELETE FROM ir_translation
    WHERE name = 'res.company,mail_signature_template' AND type = 'model';
    """

    # Add the QoQa.ch default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'sale.shop,mail_signature_template', '2', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qoqa.ch/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_2_v2.png" alt="QoQa.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041216332080" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 21 633 20 80</a>
                <a href="http://www.qoqa.ch/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model'),
    ('de_DE', 'sale.shop,mail_signature_template', '2', 'translated', '
    <p>Freundliche Grüsse,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qoqa.ch/de/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_2_v2.png" alt="QoQa.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041445552505" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 44 555 25 05</a>
                <a href="http://www.qoqa.ch/de/contact/" style="color: #BDBDBD;text-decoration: none;">Kontakt</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # Add the Qsport.ch default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'sale.shop,mail_signature_template', '4', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qsport.ch/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_7_v2.png" alt="Qsport.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041216332080" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 21 633 20 80</a>
                <a href="http://www.qsport.ch/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model'),
    ('de_DE', 'sale.shop,mail_signature_template', '4', 'translated', '
    <p>Freundliche Grüsse,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qsport.ch/de/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_7_v2.png" alt="Qsport.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041445552505" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 44 555 25 05</a>
                <a href="http://www.qsport.ch/de/contact/" style="color: #BDBDBD;text-decoration: none;">Kontakt</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # Add the Qwine.ch default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'sale.shop,mail_signature_template', '3', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qwine.ch/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_4_v2.png" alt="Qwine.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041216332080" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 21 633 20 80</a>
                <a href="http://www.qwine.ch/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model'),
    ('de_DE', 'sale.shop,mail_signature_template', '3', 'translated', '
    <p>Freundliche Grüsse,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qwine.ch/de/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_4_v2.png" alt="Qwine.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041445552505" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 44 555 25 05</a>
                <a href="http://www.qwine.ch/de/contact/" style="color: #BDBDBD;text-decoration: none;">Kontakt</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # Add the Qooking.ch default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'sale.shop,mail_signature_template', '6', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qooking.ch/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_10_v2.png" alt="Qooking.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041216332080" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 21 633 20 80</a>
                <a href="http://www.qooking.ch/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model'),
    ('de_DE', 'sale.shop,mail_signature_template', '6', 'translated', '
    <p>Freundliche Grüsse,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qooking.ch/de/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_10_v2.png" alt="Qooking.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041445552505" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 44 555 25 05</a>
                <a href="http://www.qooking.ch/de/contact/" style="color: #BDBDBD;text-decoration: none;">Kontakt</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # Add the Qstyle.ch default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'sale.shop,mail_signature_template', '5', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qstyle.ch/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_9_v2.png" alt="Qstyle.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041216332080" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 21 633 20 80</a>
                <a href="http://www.qstyle.ch/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model'),
    ('de_DE', 'sale.shop,mail_signature_template', '5', 'translated', '
    <p>Freundliche Grüsse,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qstyle.ch/de/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_9_v2.png" alt="Qstyle.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041445552505" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 44 555 25 05</a>
                <a href="http://www.qstyle.ch/de/contact/" style="color: #BDBDBD;text-decoration: none;">Kontakt</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # Add the Pepsee.ch default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'sale.shop,mail_signature_template', '15', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.pepsee.ch/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_12_v2.png" alt="Pepsee.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041216332080" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 21 633 20 80</a>
                <a href="http://www.pepsee.ch/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model'),
    ('de_DE', 'sale.shop,mail_signature_template', '15', 'translated', '
    <p>Freundliche Grüsse,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.pepsee.ch/de/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_12_v2.png" alt="Pepsee.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041445552505" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 44 555 25 05</a>
                <a href="http://www.pepsee.ch/de/contact/" style="color: #BDBDBD;text-decoration: none;">Kontakt</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # Add the QoQa.fr default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'sale.shop,mail_signature_template', '8', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qoqa.fr/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_3_v2.png" alt="QoQa.fr" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:00330556375708" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">(+33)(0)5 56 37 57 08</a>
                <a href="http://www.qoqa.fr/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.fr/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.fr</a>
            <a href="http://www.qchef.fr/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qchef.fr</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # Add the Qchef.fr default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'sale.shop,mail_signature_template', '14', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qchef.fr/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_11_v2.png" alt="Qchef.fr" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:00330556375708" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">(+33)(0)5 56 37 57 08</a>
                <a href="http://www.qchef.fr/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.fr/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.fr</a>
            <a href="http://www.qchef.fr/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qchef.fr</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """


    # Add the QoQa.fr default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'res.company,mail_signature_template', '4', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qoqa.fr/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_3_v2.png" alt="QoQa.fr" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:00330556375708" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">(+33)(0)5 56 37 57 08</a>
                <a href="http://www.qoqa.fr/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.fr/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.fr</a>
            <a href="http://www.qchef.fr/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qchef.fr</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # Add the QoQa.ch default values
    Given I execute the SQL command
    """
    INSERT INTO ir_translation
    (lang, name, res_id, state, value, type)
    VALUES
    ('fr_FR', 'res.company,mail_signature_template', '3', 'translated', '
    <p>Meilleures salutations,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qoqa.ch/fr/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_2_v2.png" alt="QoQa.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041216332080" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 21 633 20 80</a>
                <a href="http://www.qoqa.ch/fr/contact/" style="color: #BDBDBD;text-decoration: none;">Contact</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/fr/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model'),
    ('de_DE', 'res.company,mail_signature_template', '3', 'translated', '
    <p>Freundliche Grüsse,</p>
    <p>$user_signature</p>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td width="160" rowspan="2" valign="middle" style="font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif; border:none;">
                <a href="http://www.qoqa.ch/de/"><img src="http://static.qoqa.com/mobile_applications/logos/shop_header_2_v2.png" alt="QoQa.ch" width="144" height="48" border="0" /></a>
            </td>
            <td valign="middle" style="padding-left: 20px; padding-bottom: 10px; border-bottom: 1px solid #D5D5D5;border-left: 1px solid #D5D5D5; font-size:16px;font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
                <a href="tel:0041445552505" style="color: #BDBDBD;text-decoration: none; margin-right: 30px;">+41 44 555 25 05</a>
                <a href="http://www.qoqa.ch/de/contact/" style="color: #BDBDBD;text-decoration: none;">Kontakt</a>
            </td>
        </tr>
        <tr>
            <td valign="middle" style="padding-left: 20px; border-left: 1px solid #D5D5D5; font-size:16px; font-family: Helvetica, ''Helvetica Neue'', Helvetica, Arial, sans-serif;color: #BDBDBD;">
            <a href="http://www.qoqa.ch/fr" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px; border-bottom: 1px solid #D5D5D5;">QoQa.ch</a>
            <a href="http://www.qwine.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px; border-bottom: 1px solid #D5D5D5;">Qwine.ch</a>
            <a href="http://www.qsport.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qsport.ch</a>
            <a href="http://www.qooking.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px;line-height:40px;border-bottom: 1px solid #D5D5D5;">Qooking.ch</a>
            <a href="http://www.qblog.ch/de/" style="color: #BDBDBD;text-decoration:none;margin-right: 30px; line-height:40px;border-bottom: 1px solid #D5D5D5;">Qblog.ch</a>
            </td>
        </tr>
    </table>
    ', 'model');
    """

    # UPDATE EXISTING TEMPLATES
    Given I execute the SQL command
    """
    UPDATE ir_translation
    SET value = regexp_replace(value,
                               '<p>\${object\.greetings or ...Meilleures salutations...}</p>\s\s<p>\${object\.user_id\.signature or ...La loutre au taquet...}<br\/>\s\${object\.shop_id\.name or ...QoQa\.ch...}</p>', 
                               '<p>${object.mail_signature | safe}</p>')
    WHERE name LIKE 'email.template,body_html'
    """

    # UPDATE POSITIONS TO 1
    Given I execute the SQL command
    """
    UPDATE qoqa_offer_position_variant SET sequence = 1 WHERE sequence = 0;
    """

    Given I set the version of the instance to "1.1.4"
