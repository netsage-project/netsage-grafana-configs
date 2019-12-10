## Setting Up Your Environment  ( DEPRECATED )

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
git submodule update --init
```
6. Install the vagrant plugins used by the Vagrantfile in the following order:
```
vagrant plugin install vagrant-vbguest
vagrant plugin install vagrant-reload 
```

This is optional but useful for copying data from VMs.

```
vagrant plugin install vagrant-scp
```

vagrant scp grafana.ini netsage-dev:/etc/grafana/grafana.ini


## Starting the VM for the First Time

## Upgrading the OS or grafana version

Must be executed at least once to create the base image.  Once the image is built it should not be needed unless a new grafana version is released.

The base image is tagged based on the version of grafana.  The Vagrant box will named: netsage-base/$VERSION where $VERSION is the grafana version.

go into the baseBox directory and run  ./build.sh to use default values or override the default behavior by setting the version

```sh
VERSION="6.6.0" ./build.sh 
```

if everything works, you should see the new image listed under:

```sh
vagrant box list
```

and to remove the box you can simply use this command:

```sh
vagrant box remove netsage-base-6.3.5
```

## Bring up Vagrant 
Perform the following steps every time you bring up a fresh instance of the VM:

1. Start the VM. This will take several minutes as it builds ands configures the virtual machine:
```
vagrant up
```
2. You are now ready to configure your data source via the Grafana web interface.  Go to http://10.3.3.3:3000/grafana/admin/ in your browser (10.3.3.3 is the statically set private address of your local VM)
3. Login with the default username `admin` and password `admin`
4. Change the password or hit "skip" if prompted to change password
5. Click on "Data Sources" in the Configuration menu on the left hand side
6. Click *netsage* in the list of datasources
7. Enter the username and password in the `User` and `Password` fields **NOTE:** This is different from your grafana credentials
8. Click `Save and Test`. It should provide imediate feedback if things are working or not.

Assuming it worked, you can now navigate to the dashboards at http://10.3.3.3:3000/grafana and see data.

## Using the VM

* SSH into the VM with the command `vagrant ssh`. You will be logged-in as the user *vagrant* and have passwordless `sudo` access.
* The `/vagrant` directory is a shared directory between the VM and host system. It is the top-level of the source tree and any changes made to the files on the host system will also happen in the VM and vice-versa. 
* If you want to shutdown the VM run `vagrant halt`
* If you want to startup the VM run `vagrant up`
* If you want to completely erase the VM run `vagrant destroy`

## Making Changes

There are two ways you can make changes
1. By editing the files in git directly and exporting them to your local instance
2. By editing the configuration through Grafana and importing them into git.

### 1. Editing the Source Code in Git and Exporting to Grafana

When you make a change to one or more of the json files under `dashboards` directly (for example : bandwidth-dashboard.json), you can copy it to the local grafana instance by running either `wizzy export dashboard bandwidth-dashboard` if you changed a single dashboard or `wizzy export dashboards` if you changed one or more dashboards. This command is to be run when you SSH into the VM using `vagrant ssh` and then moving to the vagrant folder using `cd /vagrant/`

### 2. Editing the Source Code in Grafana and Importing to Git 

If you use grafana to edit the dashbaord(s), for example : bandwidth-dashboard, you can copy the changes back to git by running either `wizzy import dashboard bandwidth-dashboard` if you changed a single dashboard or `wizzy import dashboards` if you changed one or more dashboards. This command is to be run when you SSH into the VM using `vagrant ssh` and then moving to the vagrant folder using `cd /vagrant/`

Then, you would be able to see the changes when you run a `git status` command where you have cloned the `netsage-grafana-configs` directory.

