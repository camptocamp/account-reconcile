# How to use a integration in DEV mode

## Get a dump locally

If you already have a local dump on your computer, you can skip this section.
If the project is not hosted on our cloud-platform, you should ask a dump to the support team or the project manager.

0. Look before if one dump is not already available on dump-bag

1. Connect to production replication server on odoo-platform-none-db-replication

    Make sure you're in C2C VPN and open a terminal.

    ```
    ssh -C -A -p 2222 tunnel@tunnel.ssh.qoqa-odoo.infrastructure.qoqa.ninja -L 7555:master.database-int:5432 -N
    ```

    This will create a connection to DB server on localhost:7555


2. Create and download the dump

    Open a second terminal.

    Be sure you have ```pg_dump (PostgreSQL) 9.6.9``` with command ```pg_dump --version```
    otherwise [update you PostgreSQL version](https://askubuntu.com/questions/831292/how-do-i-install-postgresql-9-6-on-any-ubuntu-version)

    ```
    pg_dump --format=c -h localhost -p 7555 -U qoqa_odoo_integration qoqa_odoo_integration -O --file qoqa-int-$(date +%Y-%m-%d).pg
    ```

    And password is on LastPass

    [Push dump on dump-bag](https://dump-bag.odoo.camptocamp.ch/help#push-dump-on-s3)

## [Using the production dump](https://github.com/camptocamp/qoqa_openerp/blob/master/docs/how-to-use-a-prod-db-in-dev.md)


## Notes

* [How to work with several databases](./docker-dev.md#working-with-several-databases)
* [How to restore a dump](./how-to-backup-and-restore-volumes.md#restore-a-dump)
