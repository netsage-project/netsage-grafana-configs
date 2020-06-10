---
id: regression
title: Regression Testing
sidebar_label: Regression Testing
---
# Regression Testing

## Install Cypress

```sh
yarn install 
```

or 

```sh
npm install 
```

After which the binary should be install in node_modules/.bin/

## Setup Dashboard

You will need the dashboard to be up and running.  please bring it up via ```docker-compose up -d ``` and import the dashboards and datasources with wizzy

## Running Tests

The regression tests extracts the credentials from environment variables so you should run it with the following set:

```sh
CYPRESS_GRAFANA_USER="CHANGE_ME" CYPRESS_GRAFANA_PASSWORD="CHANGEME" ./node_modules/.bin/cypress open
```

Every test should start with issuing the ```cy.login()``` command follow by a typical test.

Please see this working [example](../cypress/integration/integration/flow_analysis.js)

If you fail to do so, the environment_validation check will let you know.

## Travis

To run the regression on travis please create a custom build and paste in the content of travis-regression.yaml.


In the future, we'll have a regular cron that will execute these tests on a regular basis. 

