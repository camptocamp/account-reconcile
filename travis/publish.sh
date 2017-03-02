#!/bin/bash -e

set -e

function deploy {
    local environment=$1

    wget -O - http://releases.rancher.com/compose/beta/v0.7.2/rancher-compose-linux-amd64-v0.7.2.tar.gz |\
        tar -x -z -C ${HOME} && mv ${HOME}/rancher-compose*/rancher-compose ${HOME}/ || exit $?

    RANCHER_COMPOSE="${HOME}/rancher-compose"
    TEMPLATE_DIR="${TRAVIS_BUILD_DIR}/rancher/${environment}"

    source <(echo $rancher_env_password | gpg --passphrase-fd 0 --decrypt --no-tty $TEMPLATE_DIR/rancher.env.gpg)

    (cd "${TEMPLATE_DIR}" && \
     ${RANCHER_COMPOSE} -p "${RANCHER_STACK_NAME}" rm odoo db --force && \
     sleep 30 && \
     ${RANCHER_COMPOSE} -p "${RANCHER_STACK_NAME}" up --pull --recreate --force-recreate --confirm-upgrade -d)
}

if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
  docker login --username="$DOCKER_USERNAME" --password="$DOCKER_PASSWORD"

  if [ "$TRAVIS_BRANCH" == "9.0" ]; then
    echo "Deploying image to docker hub for master (latest)"
    docker tag qoqa_odoo camptocamp/qoqa_openerp:latest
    docker push "camptocamp/qoqa_openerp:latest"
    echo "Building test server"
    # deploy latest
  elif [ ! -z "$TRAVIS_TAG" ]; then
    echo "Deploying image to docker hub for tag ${TRAVIS_TAG}"
    docker tag qoqa_odoo camptocamp/qoqa_openerp:${TRAVIS_TAG}
    docker push "camptocamp/qoqa_openerp:${TRAVIS_TAG}"
  elif [ ! -z "$TRAVIS_BRANCH" ]; then
    echo "Deploying image to docker hub for branch ${TRAVIS_BRANCH}"
    docker tag qoqa_odoo camptocamp/qoqa_openerp:${TRAVIS_BRANCH}
    docker push "camptocamp/qoqa_openerp:${TRAVIS_BRANCH}"
  else
    echo "Not deploying image"
  fi
fi
