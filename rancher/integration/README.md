# Integration templates

That will change!

For now, you have to export the following variables:

```

export RANCHER_URL=https://caas.camptocamp.net
export RANCHER_ACCESS_KEY=# create an api key
export RANCHER_SECRET_KEY=# create an api key

export DB_NAME=qoqa_int
export DB_USER=openerp
export DB_PORT=5432
export DB_PASSWORD=# see in lastpass ("QoQa RDS")
export ADMIN_PASSWD=# set an admin password (anything, we don't use it)
export RUNNING_ENV=integration
export DEMO=none
export WORKERS=6
export MAX_CRON_THREADS=2
export LOG_LEVEL=info
export LOG_HANDLER=:INFO
export DB_MAXCONN=64
export LIMIT_MEMORY_SOFT=2147483648
export LIMIT_MEMORY_HARD=2684354560
export LIMIT_REQUEST=8192
export LIMIT_TIME_CPU=86400
export LIMIT_TIME_REAL=86400
export ODOO_CONNECTOR_CHANNELS=root:3,root.connector_qoqa.fast:1,root.connector_qoqa.normal:1

```

The command to start the stack is 

```
rancher-compose -p qoqa-odoo-integration up -d
```

## Process to setup the integration server:

Warning: this process needs testing.

Things to check:

* In `docker-compose.yml`, verify that the tag of the image is the correct one
  (such as camptocamp/qoqa_openerp:9.1.0)

Assuming you already have a pg dump:

1. source the variables above
2. stop the services

  ```
  rancher-compose -p qoqa-odoo-integration stop
  rancher-compose -p qoqa-odoo-integration rm odoo --force
  ```

3. `scp` the dump on a qoqa server (so we have access to the RDS server)

  ```
  scp ~/nobackup/backups/qoqa/db.pg openerp@test.erp.qoqa.com:/srv/openerp
  ``m

4. `ssh` on the server

  ```
  ssh openerp@test.erp.qoqa.com
  ```
  
5. drop the database:

  ```
  dropdb -h odoo-database-qoqaint.c67s1aro4oyt.eu-west-1.rds.amazonaws.com qoqa_int
  ```
  
6. create the database:

  ```
  createdb -h odoo-database-qoqaint.c67s1aro4oyt.eu-west-1.rds.amazonaws.com -O openerp -Uopenerp qoqa_int
  ```
  
7. open a tmux (important because the dump is really slow to load)

   ```
   pg_restore -O -j2 -h odoo-database-qoqaint.c67s1aro4oyt.eu-west-1.rds.amazonaws.com -d qoqa_int -U openerp db.pg
   ```

8. TODO: see if restoring the filestore is required and document this step
   
8. Once loaded, start the services
```
rancher-compose -p qoqa-odoo-integration up --pull --recreate --force-recreate --confirm-upgrade -d
```
