# netsage-grafana-configs

This repository contains the dashboard configuration files used by NetSage. The configuration files are managed using a tool called [wizzy](https://github.com/utkarshcmu/wizzy). A [Vagrantfile](https://www.vagrantup.com) is provided that sets-up a CentOS 7 environment with Grafana and wizzy installed. The Vagrantfile also installs panel and datasource plug-ins used by NetSage, some of which are included as git submodules in the `plugins` directory. For everything to work properly make sure you pull down the submodules when you clone the repository. You can do so with the following commands:

```
git clone --recursive https://github.com/netsage-project/netsage-grafana-configs
```
OR
```
git clone https://github.com/netsage-project/netsage-grafana-configs
gitsubmodule init
git submodule update
```

## Using the Vagrant VM

The provided Vagrant VM allows you to run a local NetSage instance. To start the VM run:

```
vagrant up
```
Once setup is complete, you will need to configure authentication information for the `netsage` data source with the following steps:

1. Go to http://10.3.3.3:3000/datasources in your browser (10.3.3.3 is the statically set private address of your local VM)
2. Login with the default username `admin` and password `admin`
3. Change the password or hit "skip" if prompted to change password
4. Click *netsage* in the list of datasources
5. Enter the username and password in the `User` and `Password` fields
6. Click `Save and Test`. It should provide imediate feedback if things are working or not.

Assuming it worked, you can now navigate to the dashboards at http://10.3.3.3:3000/ and see data. 

## wizzy configuration
The repo includes a file `conf/wizzy.json.default` that has a set of environments defined that point at different grafana installations. It has the default context (i.e. the active environment) set to `local` which points at the local grafana instance running on the VM. When the VM is created, `conf/wizzy.json.default` is copied to `conf/wizzy.json`. The copy is ignored by git, so if there are any changes you want to commit, they need to be done to `conf/wizzy.json.default` (this protects against iadvertently commiting local changes). The currently defined environments are:

 * **local** - points at the local grafana server with default credentials
 * **international** - points at the NetSage international dashboard with no credentials (i.e. read-only)

## Importing a remote dashboard
The commands below download all the dashboards from the grafana instance in the selected context.

```
wizzy set context grafana ENVIRONMENT_NAME
wizzy import dashboards
```

For example, if you want to pull down changes that were made to the international deployment outside of git then run the following:

```
wizzy set context grafana international
wizzy import dashboards
```

## Exporting changes to the local grafana instance

If you make changes to the git repo dashboard files under the `dashboards` directory, you can install them on the local instance with the following (note: the first command is optional if using the default wizzy configuration):

```
wizzy set context grafana local
wizzy export dashboards
```


