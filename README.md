# netsage-grafana-configs

This repository contains the dashboard configuration files used by NetSage. The configuration files are managed using a tool called [wizzy](https://github.com/utkarshcmu/wizzy). A [Vagrantfile](https://www.vagrantup.com) is provided that sets-up a CentOS 7 environment with Grafana, wizzy, and required plugins to run a full NetSage instance. 

## Setting Up Your Environment

Prepare your development system with the following steps:

1. Install VirtualBox by following the instructions for your operating system [here](https://www.virtualbox.org/wiki/Downloads)
2. Install Vagrant by following the instructions for your operating system [here](https://www.vagrantup.com/downloads.html)
3. Clone this repository using the command(s) below:
```
git clone https://github.com/netsage-project/netsage-grafana-configs
```
4. Change your working directory to the git repository you just cloned:
```
cd netsage-grafana-configs
```
5. Pull down the submodules found in the plug-ins directory:
```
gitsubmodule init
git submodule update
```
6. Install the vagrant plugins used by the Vagrantfile
```
vagrant plugin install vagrant-reload vagrant-vbguest
```

## Starting the VM for the First Time

Perform the following steps every time you bring up a fresh instance of the VM:

1. Start the VM. This will take several minutes as it builds ands configures the virtual machine:
```
vagrant up
```
2. You are now ready to configure your data source via the Grafana web interface.  Go to http://10.3.3.3:3000/admin in your browser (10.3.3.3 is the statically set private address of your local VM)
3. Login with the default username `admin` and password `admin`
4. Change the password or hit "skip" if prompted to change password
5. Click on "Data Sources" in the Configuration menu on the left hand side
6. Click *netsage* in the list of datasources
7. Enter the username and password in the `User` and `Password` fields
8. Click `Save and Test`. It should provide imediate feedback if things are working or not.

Assuming it worked, you can now navigate to the dashboards at http://10.3.3.3:3000/ and see data.

## Using the VM

* SSH into the VM with the command `vagrant ssh`. You will be logged-in as the user *vagrant* and have passwordless `sudo` access.
* The `/vagrant` directory is a shared directory between the VM and host system. It is the top-level of the source tree and any changes made to the files on the host system will also happen in the VM and vice-versa. 
* If you want to shutdown the VM run `vagrant halt`
* If you want to startup the VM run `vagrant up`
* If you want to completely erase the VM run `vagrant destroy`

## Making Changes

There are two ways you can make changes: by editing the files in git directly and exporting them to your local instance or editing the configuration through Grafana and importing them into git. Instrcutions for each method below.

### Editing the Source Code in Git and Exporting to Grafana

If you make a change to one of the files under `dashboards` directly, you can copy it to the local grafana instance by running `wizzy export dashboards`. 

### Editing the Source Code in Grafana and Importing to Git 

If you use grafana to edit the dashbaords, you can copy the changes back to git by running `wizzy import dashboards`. 

## Appendix: Plugin Submodules

A number of external plugins are included using git submodules. The way submodules work is they point at a specific commit of a remote git repository. The fact that it points at a specific commit allows us to also control what version of the plugin we are using without worrying about what changes are occuring in the external repository. It also allows us to maintain a history of which versions of the grafana configurations used which versions of the plugins. 

The submodules have a number of nice features but can sometimes be a little confusing. A couple tips to keep in mind:

* In general, never commit changes to files contained within a submodule. The only thing that should be changing over time is the external commit at which the submodules point. Merges can get really confusing/impossible if you violate this principle. 
* If you want to update a submodule to point at the latest version of the git tree it currently references you can do so as follows (using netsage-sankey-plugin as an example)

```
cd plugins/netsage-sankey-plugin
git pull
cd ../../
git add plugins/netsage-sankey-plugin
git commit -m "Updating plugins/netsage-sankey-plugin to latest committed version"
```
* If you want to update a submodule to point at a different branch you can do so as follows: 

```
cd plugins/netsage-sankey-plugin
git fetch
git checkout BRANCH
git add plugins/netsage-sankey-plugin
git commit -m "Updating plugins/netsage-sankey-plugin to pint at branch BRANCH"
```
* If you update a module and want to use the updated module on you local instance you will need to reinstall it. This process is plugin dependent but usually consists of running `make install` from the submodule directory and `systemctl restart grafana-server` or similar. 

## Appendix: Wizzy Reference

### wizzy configuration
The repo includes a file `conf/wizzy.json.default` that has a set of environments defined that point at different grafana installations. It has the default context (i.e. the active environment) set to `local` which points at the local grafana instance running on the VM. When the VM is created, `conf/wizzy.json.default` is copied to `conf/wizzy.json`. The copy is ignored by git, so if there are any changes you want to commit, they need to be done to `conf/wizzy.json.default` (this protects against iadvertently commiting local changes). The currently defined environments are:

 * **local** - points at the local grafana server with default credentials
 * **international** - points at the NetSage international dashboard with no credentials (i.e. read-only)

### Importing a remote dashboard
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

### Exporting changes to the local grafana instance

If you make changes to the git repo dashboard files under the `dashboards` directory, you can install them on the local instance with the following (note: the first command is optional if using the default wizzy configuration):

```
wizzy set context grafana local
wizzy export dashboards
```


