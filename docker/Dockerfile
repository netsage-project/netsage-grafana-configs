FROM grafana/grafana:6.3.5

USER root

RUN apt-get update && \ 
    apt-get install -y python rsync python3 python3-pip git-core vim netcat sudo alien rpm && \
    pip3 install --upgrade pip && \
    apt-get clean && \
    mkdir /vagrant  
    
## Build base image
COPY . /vagrant

## Install super old NodeJS for backward compatibility and force extra old version to be installed
RUN cp /vagrant/docker/00_preferences /etc/apt/preferences.d/ && \
    curl -sL https://deb.nodesource.com/setup_6.x | bash - && \
    apt-get update && apt-get install -y nodejs && \
    npm -g install yarn 


# Fix the Makefile scripts
RUN  cd /vagrant/docker; ./docker_fix_build.sh
RUN /vagrant/docker/setup_dashboard-docker.sh

COPY docker/docker-sync.sh /usr/local/bin/

WORKDIR /vagrant 

VOLUME /vagrant

CMD /run.sh 
