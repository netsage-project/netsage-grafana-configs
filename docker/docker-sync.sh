#!/usr/bin/env bash
cd /vagrant

CREDS=/vagrant/local.env
if test -f "$CREDS"; then
    source $CREDS
    sed -i -e "s/\"user\":.*/\"user\": \"$cred_user\",/" -e  "s/\"password\":.*/\"password\": \"$cred_pwd\",/"   datasources/netsage.json
fi 


cp -f conf/wizzy.json.default conf/wizzy.json

wizzy set context grafana local #this should be the default, but just in case
wizzy export dashboards
wizzy export datasources
