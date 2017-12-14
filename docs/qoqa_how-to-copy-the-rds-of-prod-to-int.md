# How to copy the RDS of production to integration

* Before starting: Ask the infrastructure Team to make a snapshot of the production to integration.
  In that copy you shall find the prod db `qoqa_odoo_prod`
  NB: They have been asking to stop INT before they make the copy
  NB2: We have now access 3 commands for snapshot "management" go to next chapter

1. Stop the services

  In the qoqa-rancher-template repo, stop the services

2. Connect to the environment. N.B: unless the cloud-platform, you won't have a promt opening
```
qoqa-platform-int-db 9451
```
in another shell
```
psql -p 9451 -h localhost -U postgres postgres
```
Launch the following commands

```
\c template1
```
- terminate connections on integration
```
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'qoqa_odoo_integration'
  AND pid <> pg_backend_pid();
```
- terminate connections on prod
```
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'qoqa_odoo_prod'
AND pid <> pg_backend_pid();
```
- rename to have a new one
```
ALTER DATABASE qoqa_odoo_prod RENAME TO qoqa_odoo_integration;
```
- Give access back to the right user
```
GRANT ALL ON DATABASE qoqa_odoo_integration to qoqa_odoo_integration;
GRANT ALL ON SCHEMA public to qoqa_odoo_integration;
REASSIGN owned by qoqa_odoo_prod to qoqa_odoo_integration ;
\c qoqa_odoo_integration
REASSIGN owned by qoqa_odoo_prod to qoqa_odoo_integration ;
```

3. Restart Integration

 In the qoqa-rancher-template repo start services


4. Into the Integration databse we need to update the optimizations

```
VACUUM ANALYZE;
```


# Usefull RDS commands

aws --profile foo rds describe-db-snapshots --db-instance-identifier <NAME>
aws --profile foo rds create-db-snapshot --db-instance-identifier <NAME>
--db-snapshot-identifier <NAME>
aws --profile foo rds delete-db-snapshot --db-snapshot-identifier <NAME>

Contenu de ~/.aws/config:
[profile foo]
region = eu-west-1

Contenu de ~/.aws/credentials
[foo]
aws_access_key_id = key_id
aws_secret_access_key = private_key
