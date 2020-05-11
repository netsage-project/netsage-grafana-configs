#!/usr/bin/env bash
set -em

bash /run.sh  & 

until nc -z -v -w30 localhost 3000
do
  echo "Waiting 5 second until grafana is coming up..."
  # wait for a second before checking again
  sleep 5
done

echo "Importing dashboards"
/usr/bin/docker-sync

fg %1
