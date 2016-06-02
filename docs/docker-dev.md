# Working on the project as developers

## Pre-requisite

Be sure to [install Docker and docker-compose](prerequisites.md) before going any further.

## Starting, git submodules

1. Clone the project

        git clone git@github.com:camptocamp/qoqa_openerp.git qoqa

2. Clone the submodules

```bash
git submodule init
git submodule update
```

If you have an error because a ref cannot be found, it is probably that the
remote has change, you just need to run the following command that will update
the remote:

```bash
git submodule sync
```

## Docker

### Build of the image

In a development environment, building the image is rarely necessary. The
production images are built by Travis. Furthermore, In the development
environment we share the local (source code) folders with the container using
`volumes` so we don't need to `COPY` the files in the container.

Building the image is required when:

* you start to work on the project
* the base image (`camptocamp/odoo-project:9.0`) has been updated and you need
  the new version
* the local Dockerfile has been modified (for example when dependency or addons
  repository is added)

Building the image is a simple command:

```bash
# build the docker image locally (--pull pulls the base images before building the local image)
docker-compose build --pull   
```

You could also first pull the base images, then run the build:

```bash
docker-compose pull
docker-compose build
```


### Usage

When you need to launch the services of the composition, you can either run them in foreground or in background.

```bash
docker-compose up
```
Will run the services (postgres, odoo, nginx) in foreground, mixing the logs of all the services.

```bash
docker-compose up -d
```
Will run the services (postgres, odoo, nginx) in background.

When it is running in background, you can show the logs of one service or all of them (mixed):

```bash
docker-compose logs odoo      # show logs of odoo
docker-compose logs postgres  # show logs of postgres
docker-compose logs nginx     # show logs of nginx
docker-compose logs           # show all logs
```

And you can see the details of the running services with:

```bash
docker-compose ps
```

In the default configuration, the Odoo port changes each time the service is
started.  Some prefer to always have the same port, if you are one of them, you
can create your own configuration file or adapt the default one locally.

To know the port of the running Odoo, you can use the command `docker ps` that
shows information about all the running containers or the subcommand `port`:

```bash
docker ps
docker-compose port odoo 8069  # for the service 'odoo', ask the corresponding port for the container's 8069 port
```

This command can be used to open directly a browser which can be nicely aliased (see later).

```bash
export BROWSER="chromium-browser --incognito" # or firefox --private-window
$BROWSER $(docker-compose port odoo 8069)
```

Last but not least, we'll see other means to run Odoo, because `docker-compose
up` is not really good when it comes to real development with inputs and
interactions such as `pdb`.

**docker exec** (or `docker-compose exec` in the last versions of docker-compose)
allows to *enter* in a already running container, which can be handy to inspect
files, check something, ... 

```bash
# open the database (the container name is found using 'docker ps')
docker exec -ti qoqa_db_1 psql -U odoo odoodb  
# run bash in the running odoo container
docker exec -ti qoqa_openerp_1 bash
```

**docker run** spawns a new container for a given service, allowing the
interactive mode, which is exactly what we want to run Odoo with pdb.
This is probably the command you'll use the more often.

The `--rm` option drops the container after usage, which is usually what we
want.

```bash
# start Odoo
docker-compose run --rm odoo odoo.py --workers=0 ... additional arguments
# start Odoo and expose the port 8069 to the host on the same port
docker-compose run --rm -p 8069:8069 odoo odoo.py
# open an odoo shell
docker-compose run --rm odoo odoo.py shell  
```


Finally, a few aliases suggestions:

```bash
alias doco='docker-compose'
alias docu='docker-compose up -d'
alias docl='docker-compose logs'
alias docsh='docker-compose run --rm odoo ./src/odoo.py shell'
alias bro='chromium-browser --incognito $(docker-compose port odoo 8069)'
```

Usage of the aliases / commands:
```bash

# Start all the containers in background
docu

# Show status of containers
doco ps

# show logs of odoo or postgres
docl odoo
docl db

# run a one-off command in a container
doco run --rm odoo bash

# open a chromium browser on the running odoo
bro

# stop all the containers
doco stop

```

Note: if you get the following error when you do `docker-compose up`:

    ERROR: Couldn't connect to Docker daemon at http+docker://localunixsocket - is it running?

    If it's at a non-standard location, specify the URL with the DOCKER_HOST environment variable.

Know that it has been reported: https://github.com/docker/compose/issues/3106

