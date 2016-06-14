#!/bin/bash -e

set -e

function deploy {
    local version=$1

    wget -O - http://releases.rancher.com/compose/beta/v0.7.2/rancher-compose-linux-amd64-v0.7.2.tar.gz |\
        tar -x -z -C ${HOME} && mv ${HOME}/rancher-compose*/rancher-compose ${HOME}/ || exit $?
    RANCHER_COMPOSE="${HOME}/rancher-compose"
    TEMPLATE_DIR="${PWD}/rancher/template/${version}"
    openssl aes-256-cbc -K $encrypted_deb6d4f0542c_key -iv $encrypted_deb6d4f0542c_iv -in .rancher.env.enc -out .rancher.env -d
    (. "$HOME/.rancher.env" ; cd "${TEMPLATE_DIR}" && \
     ${RANCHER_COMPOSE} -p "${RANCHER_PROJECT_NAME}" rm --force && \
     sleep 30 && \
     ${RANCHER_COMPOSE} -p "${RANCHER_PROJECT_NAME}" up --pull --recreate --force-recreate --confirm-upgrade -d)
}

if [ "$TRAVIS_PULL_REQUEST" == "false" ]; then
  docker login --username="$DOCKER_USERNAME" --password="$DOCKER_PASSWORD"

  if [ "$TRAVIS_BRANCH" == "9.0" ]; then
    echo "Deploying image to docker hub for master (latest)"
    docker tag qoqa_odoo camptocamp/qoqa_openerp:latest
    docker push "camptocamp/qoqa_openerp:latest"
    echo "Building test server"
    deploy dev
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
