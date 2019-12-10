#!/usr/bin/env bash
cd /vagrant

cp -f conf/wizzy.json.default conf/wizzy.json

wizzy set context grafana local #this should be the default, but just in case
wizzy export dashboards
wizzy export datasources

