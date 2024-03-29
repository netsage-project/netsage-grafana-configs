FROM grafana/grafana:8.2.7-ubuntu

USER root

RUN apt-get update && \ 
    apt-get install -y python rsync python3 python3-pip git-core vim netcat sudo alien rpm netcat && \
    pip3 install --upgrade pip && \
    apt-get clean && \
    mkdir /app  && \
    groupadd grafana && \
    gpasswd -a grafana grafana

## Build base image
COPY . /app

## Install super old NodeJS for backward compatibility and force extra old version to be installed
RUN cp /app/docker/00_preferences /etc/apt/preferences.d/ && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get update && apt-get install -y nodejs && \
    npm -g install yarn 


# Fix the Makefile scripts
RUN  cd /app/docker; ./docker_fix_build.sh && \
    /app/docker/setup_dashboard.sh && \
    cp /app/docker/docker-sync.sh /usr/bin/docker-sync && \
    cp /app/docker/grafana_runner.sh  /usr/bin/grafana_runner && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

WORKDIR /app 
VOLUME /app
USER grafana 

ENV GF_PLUGINS_ALLOW_LOADING_UNSIGNED_PLUGINS=netsage-bumpchart-panel,netsage-sankey,netsage-nav-plugin,globalnoc-tsds-datasource,netsage-migrationmap,globalnoc-networkmap-panel,netsage-slopegraph-panel

ENTRYPOINT [ "/usr/bin/grafana_runner" ]

