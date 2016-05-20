[![Build Status](https://travis-ci.com/camptocamp/qoqa_odoo.svg?token=3A3ZhwttEcmdqp7JzQb7&branch=master)](https://travis-ci.com/camptocamp/qoqa_odoo)

# qoqa Odoo

This project uses Docker.
Travis builds a new image for each change on the branches and for each new tag.

The images built on the master branch are built as `camptocamp/qoqa_odoo:latest`.
The images built on other branches are built as `camptocamp/qoqa_odoo:<branch-name>`.
The ones built from tags are built as `camptocamp/qoqa_odoo:<tag-name>`.

Images are pushed on the registry only when Travis has a green build.

The database is automatically created and the migration scripts
automatically run.

## Prerequisite

Be sure to have a recent version of docker and docker-compose.


1. to install docker, refers to [this
   documentation](https://docs.docker.com/engine/installation/linux/ubuntulinux/),
   or kindly ask to someone who will be glad to help you :)
2. to install docker-compose, run

        sudo pip install docker-compose


## Project managers / testers

1. Clone the project

        git clone git@github.com:camptocamp/qoqa_odoo.git qoqa

2. Login to Docker Hub (create an account on https://hub.docker.com/ if you
   don't have one yet and ask to be added to the camptocamp team because this
   is a private project)

        docker login
        # answer to the questions

3. Start the composition

        cd qoqa
        docker-compose -f test.yml -f local.yml pull
        docker-compose -f test.yml -f local.yml up

4. Open a browser on http://localhost (only one odoo instance at a time can be
   started because it uses the port 80, this can be changed in the
   configuration file if needed)

4. In `test.yml` you might want to adapt the odoo `image` version.

5. If you want to drop your database, run:

        docker-compose -f test.yml -f local.yml rm -v

## Development

### Starting, git submodules

1. Clone the project

        git clone git@github.com:camptocamp/qoqa_odoo.git qoqa

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

### Docker

#### Build of the image

In a development environment, building the image is rarely necessary. The
production images are built by Travis. Furthermore, In the development
environment we share the local (source code) folders with the container using
`volumes` so we don't need to `COPY` the files in the container.

Building the image is required when:

* you start to work on the project
* the base image (`camptocamp/odoo-project:9.0`) has been updated and you need the new version
* the local Dockerfile has been modified

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


#### Usage

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
docker-compose odoo      # show logs of odoo
docker-compose postgres  # show logs of postgres
docker-compose nginx     # show logs of nginx
docker-compose logs      # show all logs
```

And you can see the details of the running services with:

```bash
docker-compose ps
```

In the default configuration, the Odoo port changes each time the service is
started.  Some prefer to have always the same port, if you are one of them, you
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
docker exec -ti qoqa_odoo_1 bash
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


## Deployment

As we use GitHub private repositories and the private Docker Hub, you must be
able to connect to both of them.

### Docker
```bash
docker login
# answer to the questions
```

### GitHub

Ensure to have a private SSH key with the authorizations to connect to our
private GitHub.  You can also spare to clone the repository and only transfer
the `test.yml` file.

### Deploy

The first time:
```bash
git clone git@github.com:camptocamp/qoqa_odoo.git -b 9.0.4 qoqa-test  # use the tag you want to deploy
cd qoqa-test
docker-compose -f test.yml up -d
```

For the next times:

If the application is not yet in production and you need to delete the database
to run again the setup scenario, you have to run (**it drops the database, be
cautious**):
```bash

# DO NOT RUN THIS ON THE DEFINITIVE PRODUCTION SERVER
docker-compose -f test.yml rm -v

```

Upgrade:
```bash
cd qoqa-test
git fetch origin
git checkout 9.0.4  # use the tag you want to deploy
docker-compose -f test.yml up -d
```
