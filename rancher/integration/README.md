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
export DB_PASSWORD=# see in lastpass ("QoQa RDS)
export SCENARIO_MAIN_TAG=qoqa
export ADMIN_PASSWD=# set an admin password (anything, we don't use it)
export RUNNING_ENV=integration

```

The command to start the stack is 

```
rancher-compose -p qoqa-odoo-integration up -d
```

