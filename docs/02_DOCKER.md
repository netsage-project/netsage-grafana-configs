## Docker Developer workflow

Every merge into a main release branch (ie. 1.4.0, 1.3.0, etc) commit will build a new image and replace the previous tag on docker hub.  

Once my code has been merged in, you can simply pull the latest version for the given tag.  

```sh
docker-compose stop; docker-compose rm 
docker-compose pull dashboard
```

Please note, that if you want to use a different version you also need to change the docker-compose.yml file to point to the correct version.

## Building Image Locally

You should never need to build a new image unless you're upgrading grafna, are adding a new plugin, updating a library and such or the integration tests failed and you need to fix the build.

If your changes are cosmetic, then a using the current image is just fine.  If you are making a system change then you can build 
an new image that reflects your changes by running:

```
docker build --tag=netsage/dashboard:1.4.0 -f docker/Dockerfile . 
```

Please keep in mind that this will replace the upstream tag.  Meaning when i build a new image it will name it netsage/dashboard:1.4.0  Once you are done testing simply do a pull again and i'tll reset back to the version from docker hub. 


```sh
docker-compose pull dashboard
```

## Volumes and other fun toys

To start the application simply run:

```sh
docker-compose up -d 
```

Grafana will come up on port 3000.  Please make sure vagrant isn't running at the same time. 

You can check the logs by running:

```sh
docker-comopse logs -f 
```

By default the current directory is mounted as /vagrant inside the docker container.  Any changes you make to the local file system are also reflected in the docker container. 

To sync the dashboards from your local file system with the running grafana instance, simply run:

```
docker-compose  exec dashboard docker-sync.sh
```

The script will essentially reset state of the wizzy config and import all the datasources + dashboards. 

If you wish to perform more advanced commands simply drop inside the grafana dashboard by executing the following command:

```
./script.docker_enter.sh dashboard
```

Simply go to /vagrant and run any commands you'd like then simply type exit to go back to the host file system.  type: exit to go back to the host system.


Once you're done developing.  You can bring down the dashboard by running.

```sh
docker-compose stop
```

If you don't remove the container the next time you start your app it'll have the same state.  If you wish to do that that's fine, but if you'd like to reset the state than ran:

```sh
docker-compose rm 
```