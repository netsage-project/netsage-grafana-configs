# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.define "netsage-dev", primary: true, autostart: true do |netsage|
    # set box to official CentOS 7 image
    netsage.vm.box = "centos/7"
    # explcitly set shared folder to virtualbox type. If not set will choose rsync 
    # which is just a one-way share that is less useful in this context
    netsage.vm.synced_folder ".", "/vagrant", type: "virtualbox"
    # Set hostname
    netsage.vm.hostname = "netsage-dev"
    
    # Enable IPv4. Cannot be directly before or after line that sets IPv6 address. Looks
    # to be a strange bug where IPv6 and IPv4 mixed-up by vagrant otherwise and one 
    #interface will appear not to have an address. If you look at network-scripts file
    # you will see a mangled result where IPv4 is set for IPv6 or vice versa
    netsage.vm.network "private_network", ip: "10.3.3.3"
    
    #Disable selinux
    netsage.vm.provision "shell", inline: <<-SHELL
        sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
    SHELL
    
    #reload VM since selinux requires reboot. Requires `vagrant plugin install vagrant-reload`
    netsage.vm.provision :reload

    #Install all requirements and perform initial setup
    netsage.vm.provision "shell", path: "scripts/setup_dashboard.sh"

   end
end
