---
id: docker
title: Docker Dev Guide
sidebar_label: Docker Dev Guide
---
## 1. Setting Up Your Environment 

Prepare your development system with the following steps:

1. Install Docker by following this [guide](https://docs.docker.com/install/)
2. Clone this repository using the command(s) below:

```sh
git clone https://github.com/netsage-project/netsage-grafana-configs
```

3. Change your working directory to the git repository you just cloned:

```sh
cd netsage-grafana-configs
```

4. Pull down the submodules found in the plug-ins directory:

```sh
git submodule update --init
```

## 2. Starting docker container for the First Time

1. Start the container

```sh
docker-compose up -d dashboard
```

If you need to, you can view the logs by running:

```sh
docker-compose logs -f 
```

`-f` allows you to follow the logs, or omit `-f` to simply see the current state.

2. Configure the datasource

You are now ready to configure your data source via the Grafana web interface. Go to http://localhost:3000/admin/ in your browser.

4. Login with the default username `admin` and password `admin`
5. Change the password or hit "skip" if prompted to change password
6. Click on "Data Sources" in the Configuration menu on the left hand side
7. Click *netsage* in the list of datasources
8. Enter the username and password in the `User` and `Password` fields **NOTE:** This is different from your grafana credentials
9. Click `Save and Test`. It should provide imediate feedback if things are working or not.

Assuming it worked, you can now navigate to the dashboards at http://localhost:3000/ and see data.

* The `/app` directory is a shared directory between the VM and host system. It is the top-level of the source tree and any changes made to the files on the host system will also happen in the VM and vice-versa. 
* If you want to stop the container simply run `docker-compose stop`
* If you want to startup the container again: `docker-compose up -d `
* If you want to stop the container and erase the current state you can run: `docker-compose down`

## 3. Using the docker container 

To use the docker container, you can use either Method 1 (Scripted Entry) or Method 2 (Manual Entry) as mentioned below.

### 1. Scripted Entry 

Enter the container by running the following command:
- `./scripts/docker_enter.sh netsage/dashboard` on Linux / MacOS
- `./scripts/docker_enter.PS1 netsage/dashboard` on Windows (requires powershell)

### 2. Manually entering the container:

Find the container id by running:

```sh
docker ps -a 
```

Sample output:

```sh
docker exec -it 08bba311b08d bash
```
CONTAINER ID        IMAGE                     COMMAND                  CREATED             STATUS              PORTS                    NAMES
08bba311b08d        netsage/dashboard:1.5.0   "/run.sh /bin/sh -c …"   19 minutes ago      Up 19 minutes       0.0.0.0:3000->3000/tcp   netsage-grafana-configs_dashboard_1
```

You'll need the container ID which is the first column listed.

Since we want a terminal inside the container we'll simply invoke the bash command on the container ID:

```sh
docker exec -it 08bba311b08d bash
```

This is essentially the same work that is being done by `docker_enter.sh`.  We're essentially looking for a container named 'dashboard', finding the ID and attempting to run bash to drop into a shell.

## 4. Making Changes

*If you haven't already you should make a new feature branch by running: `git checkout -b feature/new_awesome_widget`. You can use the tools found [here](https://github.com/tj/git-extras/blob/master/Commands.md#git-featurerefactorbugchore) which provide some shortcuts, such as `git feature new_awesome_widget`*

There are two ways you can make changes

1. By editing the files in git directly and exporting them to your local instance
2. By editing the configuration through Grafana and importing them into git.

### 1. Editing the Source Code in Git and Exporting to Grafana

When you make a change to one or more of the json files under `dashboards` directly (for example : bandwidth-dashboard.json), you can copy it to the local grafana instance by running either `wizzy export dashboard bandwidth-dashboard` if you changed a single dashboard or `wizzy export dashboards` if you changed one or more dashboards. This command is to be run once you enter the docker container from the `/app` folder.

### 2. Editing the Source Code in Grafana and Importing to Git 

If you use grafana to edit the dashbaord(s), for example : bandwidth-dashboard, you can copy the changes back to git by running either `wizzy import dashboard bandwidth-dashboard` if you changed a single dashboard or `wizzy import dashboards` if you changed one or more dashboards. This command is to be run once you enter the docker container from the `/app` folder.

Then, you would be able to see the changes when you run a `git status` command where you have cloned the `netsage-grafana-configs` directory.

You can find more info on using wizzy [here](04_WIZZY.md)

## 5. Advanced Docker Usage and Notes

Every merge into a main release branch (ie. 1.4.0, 1.3.0, etc) commit will build a new image and replace the previous tag on docker hub. You should not have to worry about this on a day to day basis, but if someone made an architectural change, you may pull an updated version by doing the following.

```sh
docker-compose down
docker-compose pull dashboard
```

If you want to pull a specific tag of the dashboard, you find all the current published tags: [here](https://hub.docker.com/r/netsage/dashboard/tags)

Please note, that if you want to use a different version you also need to change the docker-compose.yml file to point to the correct version.

## 6. Building Image Locally

If you are making upgrades to grafana it's a good idea to test the changes locally.

Notes:

1. `docker/setup_dashboard-docker.sh` is used to install the grafana plugins as well as the relevant wizzy version.
2. `docker/Dockerfile` pins the docker version and installs any OS level packages that you would like to be available.

To build a new image locally, you'll be replacing the current tag with the new version built locally. In order to do so, simply run the following command:

```
docker-compose build 
```


Please keep in mind that this will replace the upstream tag. This means that when I build a new image, it will name it `netsage/dashboard:1.5.0`. Once you are done testing, simply do a pull again by running the following command and it will reset back to the version from docker hub. 

```sh
docker-compose pull dashboard
```
