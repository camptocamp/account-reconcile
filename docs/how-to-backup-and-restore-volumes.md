# Backup and restore Docker Volumes

## Backup the db and filestore

```bash
$ export HOST_BACKUPS=/path/of/hosts/backups  # Where you want to save the backups
$ export DATAODOO_CONTAINER=project_dataodoo_1  # Exact name to find with docker-compose ps
$ export DATADB_CONTAINER=project_datadb_1  # Exact name to find with docker-compose ps

$ docker run --rm --volumes-from $DATAODOO_CONTAINER -v $HOST_BACKUPS:/backup debian tar cvf /backup/backup-dataodoo.tar /data/odoo
$ docker run --rm --volumes-from $DATADB_CONTAINER -v $HOST_BACKUPS:/backup debian tar cvf /backup/backup-datadb.tar /var/lib/postgresql/data
```

## Restore the db and filestore

```bash
$ docker-compose create

$ export HOST_BACKUPS=/path/of/hosts/backups  # Where you want to save the backups
$ export DATAODOO_CONTAINER=project_dataodoo_1  # Exact name to find with docker-compose ps
$ export DATADB_CONTAINER=project_datadb_1  # Exact name to find with docker-compose ps

$ docker run --rm --volumes-from $DATAODOO_CONTAINER -v $HOST_BACKUPS:/backup debian bash -c "tar xvf /backup/backup-dataodoo.tar"
$ docker run --rm --volumes-from $DATADB_CONTAINER -v $HOST_BACKUPS:/backup debian bash -c "tar xvf /backup/backup-datadb.tar"
```
