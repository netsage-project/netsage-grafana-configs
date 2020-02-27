#!/usr/bin/env bash 
set -e


function integration_test {
    docker build --tag=netsage/dashboard:latest -f docker/Dockerfile . 
    
    if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then 
        docker images 
        docker tag  netsage/dashboard:latest netsage/dashboard:$(echo ${TRAVIS_BRANCH:-testing} | sed -e "s/\//_/g") 
        ./scripts/publish_image.sh
    fi
}

function regression_test {
    if [[ "$TRAVIS_BRANCH" = "testing" ]]; then
        echo "Regression Testing not supported on PR"
    else
        echo "No Yet Implmeneted"
    fi

}

if [[ "$REGRESSION" = "true" ]]; then 
    regression_test
else
    integration_test
fi
