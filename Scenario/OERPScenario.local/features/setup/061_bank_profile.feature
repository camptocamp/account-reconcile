@bank_profile_ch @setup
Feature: BANK PROFILES

############################### COMPANY 1 ###############################

  Scenario Outline: BANK PROFILE
    Given I need a "account.statement.profile" with oid: <oid>
    And having:
    | name                  | value                    |
    | name                  | <name>                   |
    | journal_id            | by code: <name>          |
    | commission_account_id | by code: 5200            |
    | balance_check         | 1                        |
    | import_type           | generic_csvxls_so        |
    | company_id            | by oid: scenario.qoqa_ch |
   And with following rules
    | name                                                                  |
    | Match from line reference (based on Invoice number)                   |
    | Match from line reference (based on Invoice Supplier number)          |
    | Match from line reference (based on SO number)                        |
    | Match from line label (based on partner field 'Bank Statement Label') |
    | Match from line label (based on partner name)                         |

   Examples: Bank profiles for QoQa CH
     | oid                       | name  |
     | scenario.profile_ch_bnk11 | BNK11 |
     | scenario.profile_ch_bnk16 | BNK16 |
     | scenario.profile_ch_bnk15 | BNK15 |
     | scenario.profile_ch_bnk10 | BNK10 |
     | scenario.profile_ch_bnk12 | BNK12 |
     | scenario.profile_ch_bnk14 | BNK14 |
     #| scenario.profile_ch_bnk21 | BN21  |
     | scenario.profile_ch_bnk20 | BNK20 |
     | scenario.profile_ch_gar11 | GAR11 |
