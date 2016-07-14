--   Reset 'state' of ir_module_module
--
--   When we receive the database from the migration service, addons are
--   'to upgrade', set them to uninstalled.
UPDATE ir_module_module
SET state = 'uninstalled'
WHERE state IN ('to install', 'to upgrade');
