# Table of Contents

- [Setting Up Your Environment](#setting-up-your-environment)
- [Starting docker container for the First Time](#starting-docker-container-for-the-first-time)
- [Using the docker container](#using-the-docker-container)
    - [Scripted Entry](#scripted-entry)
    - [Manually entering the container:](#manually-entering-the-container)
- [Making Changes](#making-changes)
    - [1. Editing the Source Code in Git and Exporting to Grafana](#1-editing-the-source-code-in-git-and-exporting-to-grafana)
    - [2. Editing the Source Code in Grafana and Importing to Git](#2-editing-the-source-code-in-grafana-and-importing-to-git)
- [Advanced Docker Usage and Notes](#advanced-docker-usage-and-notes)
- [Building Image Locally](#building-image-locally)


---



## Setting Up Your Environment 

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


## Starting docker container for the First Time

1. Start the container

```sh
docker-compose up -d 
```

If you need to, you can view the logs by running:

```sh
docker-compose logs -f 
```

-f allows you to follow the logs, or omit -f to simply see the current state.

2. Import dashboards and data sources

The first time we run the container we need to import the dashboards and data sources.  To do so we need to run the following command.

```sh
docker-compose exec dashboard docker-sync.sh
```

3. Configure the datasource

You are now ready to configure your data source via the Grafana web interface.  Go to http://localhost:3000/grafana/admin/ in your browser.

4. Login with the default username `admin` and password `admin`
5. Change the password or hit "skip" if prompted to change password
6. Click on "Data Sources" in the Configuration menu on the left hand side
7. Click *netsage* in the list of datasources
8. Enter the username and password in the `User` and `Password` fields **NOTE:** This is different from your grafana credentials
9. Click `Save and Test`. It should provide imediate feedback if things are working or not.

Assuming it worked, you can now navigate to the dashboards at http://localhost:3000/grafana and see data.

* The `/vagrant` directory is a shared directory between the VM and host system. It is the top-level of the source tree and any changes made to the files on the host system will also happen in the VM and vice-versa. 
* If you want to stop the container simply run `docker-compose stop`
* If you want to startup the container again: `docker-compose up -d `
* If you want to stop the container and erase the current state you can run: `docker-compose up -d; docker-compose rm `


## Using the docker container 

### Scripted Entry 
* Enter the container by running the following command: 

```
./scripts/docker_enter.sh  or linux or TBD on windows.
```

### Manually entering the container:

find the container id:

```sh
docker ps -a 
```

Sample output:

```
CONTAINER ID        IMAGE                     COMMAND                  CREATED             STATUS              PORTS                    NAMES
08bba311b08d        netsage/dashboard:1.4.0   "/run.sh /bin/sh -c …"   19 minutes ago      Up 19 minutes       0.0.0.0:3000->3000/tcp   netsage-grafana-configs_dashboard_1
```

You'll need the container ID which is the first column listed.

Since we want a terminal inside the container we'll simply invoke the bash command on the container ID:

```sh
docker exec -it 08bba311b08d bash
```

This is essentially the same work that is being done by docker_enter.sh.  We're essentially looking for a container named 'dashboard', finding the ID and attempting to run bash to drop into a shell.


## Making Changes

0. If you haven't already you should make a new feature branch.  `git checkout -b feature/new_awesome_widget`.  You can use the tools found [here](https://github.com/tj/git-extras/blob/master/Commands.md#git-featurerefactorbugchore) which provide some shortcuts.  ie `git feature new_awesome_widget`

There are two ways you can make changes
1. By editing the files in git directly and exporting them to your local instance
2. By editing the configuration through Grafana and importing them into git.

### 1. Editing the Source Code in Git and Exporting to Grafana

When you make a change to one or more of the json files under `dashboards` directly (for example : bandwidth-dashboard.json), you can copy it to the local grafana instance by running either `wizzy export dashboard bandwidth-dashboard` if you changed a single dashboard or `wizzy export dashboards` if you changed one or more dashboards. This command is to be run once you enter the docker container.

### 2. Editing the Source Code in Grafana and Importing to Git 

If you use grafana to edit the dashbaord(s), for example : bandwidth-dashboard, you can copy the changes back to git by running either `wizzy import dashboard bandwidth-dashboard` if you changed a single dashboard or `wizzy import dashboards` if you changed one or more dashboards. This command is to be run once you enter the docker container.

Then, you would be able to see the changes when you run a `git status` command where you have cloned the `netsage-grafana-configs` directory.

You can find more info on using wizzy [here](04_WIZZY.md)


## Advanced Docker Usage and Notes

Every merge into a main release branch (ie. 1.4.0, 1.3.0, etc) commit will build a new image and replace the previous tag on docker hub. You should not have to worry about on a day to day basis, but if someone made an architectural change, you may pull an updated version by doing the following.


```sh
docker-compose stop; docker-compose rm 
docker-compose pull dashboard
```

If you want to pull a specific tag of the dashboard, you find all the current published tags: [here](https://hub.docker.com/r/netsage/dashboard/tags)

Please note, that if you want to use a different version you also need to change the docker-compose.yml file to point to the correct version.

## Building Image Locally

If you are making upgrades to grafana it's a good idea to test the changes locally.

Scripts of note:

1. docker/setup_dashboard-docker.sh is used to instal the grafana plugins as well as wizzy version.
2. docker/Dockerfile pins the docker version and installs any OS level packages that you'd like to be available.

to build a new image locally, you'll be replacing the current tag with the new version built locally to do so, simply run the following line:

```
docker build --tag=netsage/dashboard:1.4.0 -f docker/Dockerfile . 
```

Please keep in mind that this will replace the upstream tag.  Meaning when i build a new image it will name it netsage/dashboard:1.4.0  Once you are done testing simply do a pull again and i'tll reset back to the version from docker hub. 


```sh
docker-compose pull dashboard
```


