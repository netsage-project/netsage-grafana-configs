#!/usr/bin/env bash 
VERSION=${TRAVIS_BRANCH:-'testing'}   # Defaults to testing
VERSION=$(echo $VERSION | sed -e 's/\//_/g') # removes any / in the branch name for tagging
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
echo docker push netsage/dashboard:$VERSION
docker push netsage/dashboard:$VERSION
