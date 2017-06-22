<!--
This file has been generated with 'invoke project.sync'.
Do not modify. Any manual change will be lost.
Please propose your modification on
https://github.com/camptocamp/odoo-template instead.
-->
# Backup and restore Docker Volumes

## Backup the db and filestore (as volumes)

```bash
$ export HOST_BACKUPS=/path/of/hosts/backups  # Where you want to save the backups
$ export DATAODOO_VOLUME=project_data-odoo  # Exact name to find with 'docker volume ls'
$ export DATADB_VOLUME=project_data-db  # Exact name to find with 'docker volume ls'

$ docker run --rm -v "$DATAODOO_VOLUME:/data/odoo" -v $HOST_BACKUPS:/backup debian tar cvzf /backup/backup-dataodoo.tar.gz /data/odoo
$ docker run --rm -v "$DATADB_VOLUME:/var/lib/postgresql/data" -v $HOST_BACKUPS:/backup debian tar cvzf /backup/backup-datadb.tar.gz /var/lib/postgresql/data
```

## Restore the db and filestore (as volumes)

```bash
$ export HOST_PROJECT=/path/of/hosts/project  # Where your docker-compose.yml is
$ export HOST_BACKUPS=/path/of/hosts/backups  # Where you want to save the backups
$ export DATAODOO_VOLUME=project_data-odoo  # Exact name to find with 'docker volume ls'
$ export DATADB_VOLUME=project_data-db  # Exact name to find with 'docker volume ls'

$ cd $HOST_PROJECT
$ docker-compose stop

$ docker volume rm $DATAODOO_VOLUME
$ docker volume rm $DATADB_VOLUME

$ docker run --rm -v "$DATAODOO_VOLUME:/data/odoo" -v $HOST_BACKUPS:/backup debian bash -c "tar xvzf /backup/backup-dataodoo.tar.gz"
$ docker run --rm -v "$DATADB_VOLUME:/var/lib/postgresql/data" -v $HOST_BACKUPS:/backup debian bash -c "tar xvzf /backup/backup-datadb.tar.gz"
```

## Backup and restore with dumps

### Create a dump

If you have the same `pg_dump` version on your computer than the one used in the
db container (9.5 at time of writing), you can just use your local `pg_dump`
directly on the outgoing port of the db container (see [how to find the
port](how-to-connect-to-docker-psql.md)). Example:

```
$ pg_dump -h localhost -p 32768 --format=c -Uodoo --file db.pg odoodb
```


If you have an older version of `postgres-client`, `pg_dump` will refuse to
make a dump. An option is to update your `postgres-client`.  Here is another option using a  `postgres:9.5` one-off container (the `db` container
must be running):

```bash
$ export HOST_BACKUPS=/path/of/hosts/backups  # Where you want to save the backups
$ export PROJECT_NAME=project_name (the prefix of containers, volumes, networks, usually the root folder's name)

$ docker run --rm --net=${PROJECT_NAME}_default --link ${PROJECT_NAME}_db_1:db -e PGPASSWORD=odoo -v $HOST_BACKUPS:/backup postgres:9.5 pg_dump -Uodoo --file /backup/db.pg --format=c odoodb -h db
```

### Restore a dump

If you have the same `pg_restore` version on your computer than the one used in the
db container (9.5 at time of writing), you can just use your local `pg_restore`
directly on the outgoing port of the db container (see [how to find the
port](how-to-connect-to-docker-psql.md)). Example:

```
$ createdb -h localhost -p 32768 -O odoo prod
$ pg_restore -h localhost -p 32768 -O -U odoo -j2 -d prod
```

If you have an older version of `postgres-client`, `pg_restore` will refuse to
restore the dump. An option is to update your `postgres-client`.  Here is another option using a  `postgres:9.5` one-off container (the `db` container
must be running):

```bash
$ export HOST_BACKUPS=/path/of/hosts/backups  # From where you want to restore the backup
$ export PROJECT_NAME=project_name (the prefix of containers, volumes, networks, usually the root folder's name)

$ docker run --rm --net=${PROJECT_NAME}_default --link ${PROJECT_NAME}_db_1:db -e PGPASSWORD=odoo  postgres:9.5 createdb -h db -O odoo prod
$ docker run --rm --net=${PROJECT_NAME}_default --link ${PROJECT_NAME}_db_1:db -e PGPASSWORD=odoo -v $HOST_BACKUPS:/backup postgres:9.5 pg_restore -h db -O -U odoo --file /backup/db.pg -j2 -d prod
```
