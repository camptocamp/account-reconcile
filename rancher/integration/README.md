# Integration deployment

## Restore the new database

We restore the database with a different name, then we just switch the old one
with the new one. First, restore it:


1. `scp` the dump on the `Shell` container

  ```
  $ scp ~/path/to/db.pg your-github-user@erp-sprint.qoqa.com:~
  ```

2. SSH on the `Shell` container

  ```
  $ ssh your-github-user@erp-sprint.qoqa.com -p 2622
  ```

3. open a tmux (because the dump is slow to load)

  ```
  $ tmux
  ```
  
4. create the database with an alternative name (we'll rename)

  ```
  ~ createdb -h odoo-database-qoqaint.c67s1aro4oyt.eu-west-1.rds.amazonaws.com -O openerp -Uopenerp qoqa_int_new
  ```

5. restore the dump and only when the dump is fully restored, continue to [Switch the databases](#switch-the-databases)

   ```
   ~ pg_restore -O -j2 -h odoo-database-qoqaint.c67s1aro4oyt.eu-west-1.rds.amazonaws.com -d qoqa_int_new -U openerp db.pg
   ```

## Restore the filestore

Restoring the filestore is not documented yet. For now, we leave the current
one in place.

## Switch the databases


1. checkout the tag to deploy

  ```
  $ git checkout 9.X.Y
  ```

2. source the environment variables (password is in Lastpass: `Rancher: integration/rancher.env.gpg`)

  ```
  $ source <(gpg2 -d rancher.env.gpg)
  ```

3. stop the services (from your host)

  ```
  $ rancher-compose -p qoqa-odoo-integration stop
  ```

4. SSH on the `Shell` container and switch the databases

  ```
  $ ssh your-github-user@erp-sprint.qoqa.com -p 2622
  ~ psql -h odoo-database-qoqaint.c67s1aro4oyt.eu-west-1.rds.amazonaws.com -Uopenerp postgres -c "ALTER DATABASE qoqa_int RENAME TO qoqa_int_old"
  ~ psql -h odoo-database-qoqaint.c67s1aro4oyt.eu-west-1.rds.amazonaws.com -Uopenerp postgres -c "ALTER DATABASE qoqa_int_new RENAME TO qoqa_int"
  ```
   
5. start the services

  ```
  rancher-compose -p qoqa-odoo-integration up --pull --recreate --force-recreate --confirm-upgrade -d
  ```
  
6. On the server, drop the old database:

  ```
  $ ssh your-github-user@erp-sprint.qoqa.com -p 2622
  ~ dropdb -h odoo-database-qoqaint.c67s1aro4oyt.eu-west-1.rds.amazonaws.com -Uopenerp qoqa_int_old
  ```
