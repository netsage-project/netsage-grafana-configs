#!/usr/bin/env bash 
set -e

## Validates code and publish image for tagged branch
function integration_test {
    ## Travis keeps failing due to Limits by dockerhub, requires login 
    docker_login
    docker build --tag=netsage/dashboard:latest -f docker/Dockerfile . 
    
    if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then 
        docker images 
        docker tag  netsage/dashboard:latest netsage/dashboard:$(echo ${TRAVIS_BRANCH:-testing} | sed -e "s/\//_/g") 
        publish_image
    fi
}


function docker_login() {
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

}


## Publish image to our docker hub repository
function publish_image
{
    VERSION=${TRAVIS_BRANCH:-'testing'}   # Defaults to testing
    VERSION=$(echo $VERSION | sed -e 's/\//_/g') # removes any / in the branch name for tagging
    docker_login
    echo docker push netsage/dashboard:$VERSION
    docker push netsage/dashboard:$VERSION

}


# Sets up docker compose for regression testing
function setupDocker 
{
    sudo rm /usr/local/bin/docker-compose
    curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > docker-compose
    chmod +x docker-compose
    sudo mv docker-compose /usr/local/bin
}

## Brings up the dashboard and executes the regression tests
function cron_regression {
    if [ "$TRAVIS_EVENT_TYPE" = "cron" ]; then 
        if [ -z "$CYPRESS_GRAFANA_USER" ]; then
              echo 'CYPRESS_GRAFANA_USER is required and not set'
              exit 1
        fi
        
        if [ -z "$CYPRESS_GRAFANA_PASSWORD" ]; then
              echo 'CYPRESS_GRAFANA_PASSWORD is required and not set'
              exit 1
        fi

        setupDocker
        /usr/local/bin/docker-compose up -d 
        /usr/local/bin/docker-compose ps
        /usr/local/bin/docker-compose exec dashboard docker-sync
        ./node_modules/.bin/cypress run
        /usr/local/bin/docker-compose stop
    fi

}

# Entry point
function main
{
    if [[ "$TRAVIS_EVENT_TYPE" = "cron" ]]; then 
        cron_regression
    else
        integration_test
    fi

}

main
