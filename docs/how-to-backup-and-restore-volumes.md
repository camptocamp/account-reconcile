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
$ export HOST_BACKUPS=/path/of/hosts/backups  # Where you want to save the backups
$ export DATAODOO_VOLUME=project_data-odoo  # Exact name to find with 'docker volume ls'
$ export DATADB_VOLUME=project_data-db  # Exact name to find with 'docker volume ls'

$ docker run --rm -v "$DATAODOO_VOLUME:/data/odoo" -v $HOST_BACKUPS:/backup debian bash -c "tar xvzf /backup/backup-dataodoo.tar.gz"
$ docker run --rm -v "$DATADB_VOLUME:/var/lib/postgresql/data" -v $HOST_BACKUPS:/backup debian bash -c "tar xvzf /backup/backup-datadb.tar.gz"
```

## Backup the db in a pg dump

If you have the same `pg_dump` version on your computer than the one used in the
db container (9.5 at time of writing), you can just use your local `pg_dump`
directly on the outgoing port of the db container.

If you have another version, `pg_dump` will refuse to make a dump, here is how
you can do this with a `postgres:9.5` one-off container (the `db` container
must be running):

```bash
$ export HOST_BACKUPS=/path/of/hosts/backups  # Where you want to save the backups
$ export PROJECT_NAME=project_name (the prefix of containers, volumes, networks, usually the root folder's name)

$ docker run --rm --net=${PROJECT_NAME}_default --link ${PROJECT_NAME}_db_1:db -e PGPASSWORD=odoo -v $HOST_BACKUPS:/backup postgres:9.5 pg_dump -Uodoo --file /backup/db.pg --format=c odoodb -h db
```
