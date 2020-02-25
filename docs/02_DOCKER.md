## Docker Developer workflow

Every commit will build a new image and publish it to docker hub.  The image will be labeled based on the branch name.  If I'm working on feature/docker I can pull the docker image

```sh
docker pull netsage/dashboard:feature_docker
```

Once my code has been merged in, I can simply pull the latest version for the given tag.  

```sh
docker-compose stop; docker-compose rm 
docker pull netsage/dashboard:1.3.0
```

Please note, that if you want to use a different version you also need to change the docker-compose.yml file to point to the correct version.

## Volumes and other fun toys

By default the current directory is mounted as /vagrant inside the docker image.  Any changes you make to the local file system are also reflected in the docker container. 

To sync the dashboards from your local file system with the running grafana instance, simply run:

IMPORTANT: you need to run this command at least once in order to get the datasources and dashboards imported. 

```
docker-compose  exec dashboard docker-sync
```

The script will essentially reset state of the wizzy config and import all the datasources + dashboards. 

If you wish to perform more advanced commands simply drop into the grafana dashboard by executing the following command:

```
./script.docker_enter.sh dashboard
```

Simply go to /vagrant and run any commands you'd like then simply type exit to go back to the host file system. 

## Building Image Locally

You should never need to build a new image unless you're upgrading grafna, are adding a new plugin, updating a library and such or the integration tests failed and you need to fix the build.

If your changes are cosmetic, then a using the current image is just fine.  If you are making a system change then you can build 
an new image that reflects your changes by running:

```
docker-compose build
```

Please keep in mind that this will replace the upstream tag.  Meaning when i build a new image it will name it netsage/dashboard:1.3.0  Once you are done testing 
you need to remove the 1.3.0 tag and pull the latest from docker hub.

```sh
docker rmi netsage/dashboard:1.3.0 && docker pull netsage/dashboard:1.3.0 
```

## Saving Credentials Locally 

If you want to avoid from repeateadly entering the netsage credentials you can create a file in the root of your project named: local.env


inside the file add the following lines:

```sh
cred_user=
cred_pwd=
```

and fill in the appropriate values. If the file exists, it will use those values each time docker-sync is invoked
