#!/usr/bin/env bash
#Install wizzy
npm install -g wizzy@0.6.0

### Update grafana.ini file ###
#set default grafana theme to light
sed -i 's/^;default_theme.*/default_theme = light/' /etc/grafana/grafana.ini
#need the following setting so the google analytics script tags are not shown
sed -i 's/^;disable_sanitize_html.*/disable_sanitize_html = true/' /etc/grafana/grafana.ini
#server from /grafana subpath to match prod and dev instances behind a proxy
sed -i 's|^;root_url.*|root_url = http://localhost:3000/grafana|' /etc/grafana/grafana.ini
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
# HACK: for some reason this fails to install unless it's moved to a different location.
cp -r netsage-sankey-plugin /tmp
pushd . 
cd /tmp/netsage-sankey-plugin
make install
popd

#Install navigation
# HACK: for some reason this fails to install unless it's moved to a different location.
cp -r  NetSageNavigation /tmp/
pushd . 
cd /tmp/NetSageNavigation/
make install
popd
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
