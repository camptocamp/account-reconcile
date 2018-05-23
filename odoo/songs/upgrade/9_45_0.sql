-- Update xmlid for the stage as it was moved to another module, as it logically belongs there
-- As well as I need to use it there
UPDATE ir_model_data SET module = 'qoqa_claim' where module = 'crm_claim_mail' and name = 'stage_response_received';
