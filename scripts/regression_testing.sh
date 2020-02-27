#!/usr/bin/env bash
if [ -z "$CYPRESS_GRAFANA_USER" ]; then
      echo 'CYPRESS_GRAFANA_USER is required and not set'
      exit 1
fi

if [ -z "$CYPRESS_GRAFANA_PASSWORD" ]; then
      echo 'CYPRESS_GRAFANA_PASSWORD is required and not set'
      exit 1
fi

./node_modules/.bin/cypress run
