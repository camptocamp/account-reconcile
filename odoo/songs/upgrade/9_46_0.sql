-- Change xmlids for the partners, used in account_bank_statement_import_camt
UPDATE ir_model_data set module = 'account_bank_statement_import_camt', name = 'account_postfinance' where name = '__export__.res_partner_667295';
UPDATE ir_model_data set module = 'account_bank_statement_import_camt', name = 'account_six_payment_services' where name = '__export__.res_partner_667296';
UPDATE ir_model_data set module = 'account_bank_statement_import_camt', name = 'account_paypal' where name = '__export__.res_partner_667297';
UPDATE ir_model_data set module = 'account_bank_statement_import_camt', name = 'account_swissbilling' where name = '__export__.res_partner_865751';
UPDATE ir_model_data set module = 'account_bank_statement_import_camt', name = 'account_swisscard' where name = '__export__.res_partner_1052745';
UPDATE ir_model_data set module = 'account_bank_statement_import_camt', name = 'account_twint' where name = '__export__.res_partner_6789054';
