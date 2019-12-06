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
        sed -i s/SELINUX=enforcing/SELINUX=permissive/g /etc/selinux/config
    SHELL
    
    #reload VM since selinux requires reboot. Requires `vagrant plugin install vagrant-reload`
    netsage.vm.provision :reload

    #Install all requirements and perform initial setup
    netsage.vm.provision "shell", inline: <<-SHELL
        yum install -y epel-release
        yum clean all
        yum install -y gcc\
            kernel-devel\
            kernel-headers\
            dkms\
            make\
            bzip2\
            perl\
            perl-devel\
            net-tools\
            git\
            npm\
            rpm-build\
            gcc-c++\
            https://dl.grafana.com/oss/release/grafana-6.3.5-1.x86_64.rpm
        
        #Install wizzy
        npm install -g wizzy@0.6.0
        
        ### Update grafana.ini file ###
        #set default grafana theme to light
        sed -i 's/^;default_theme.*/default_theme = light/' /etc/grafana/grafana.ini
        #need the following setting so the google analytics script tags are not shown
        sed -i 's/^;disable_sanitize_html.*/disable_sanitize_html = true/' /etc/grafana/grafana.ini
        #server from /grafana subpath to match prod and dev instances behind a proxy
        sed -i 's/^;root_url.*/root_url = %(protocol)s:\/\/%(domain)s:3000\/grafana/' /etc/grafana/grafana.ini
        sed -i 's/^;serve_from_sub_path.*/serve_from_sub_path = true/' /etc/grafana/grafana.ini
        
        ### Start plugin installs ###
        cd /vagrant/plugins
        
        #install carpetplot
        /usr/sbin/grafana-cli plugins install petrslavotinek-carpetplot-panel
        
        #install tsds datasource plugin
        cd tsds-grafana
        npm install -g yarn #make seems to need this
        make rpm
        yum install -y $HOME/rpmbuild/RPMS/noarch/globalnoc-tsds-datasource-*.noarch.rpm
        cd ../
        
        #Install network panel plugin
        cd globalnoc-networkmap-panel
        npm install -g gulp #make seems to need this
        make rpm
        yum install -y $HOME/rpmbuild/RPMS/noarch/grnoc-grafana-worldview-*.noarch.rpm
        cd ../
        
        #Install netsage-sankey plugin
        cd netsage-sankey-plugin
        make install
        cd ../
        
        #Install navigation
        cd NetSageNavigation
        make install
        cd ../
        
        ### End plugin source code installs ###
        
        #Enable grafana
        systemctl enable grafana-server
        systemctl restart grafana-server
        
        #Set to local context
        cd /vagrant
        cp -f conf/wizzy.json.default conf/wizzy.json
        wizzy set context grafana local #this should be the default, but just in case
        wizzy export dashboards
        wizzy export datasources
        
        ##
        # This is how the github repo was built
        #wizzy init
        #wizzy set grafana url https://portal.netsage.global/grafana/
        
        ##
        # Point at local grafana instance for easy deployment
        #wizzy set grafana url http://localhost:3000
        #wizzy set grafana username admin
        #wizzy set grafana password admin
        
    SHELL
  end
end
