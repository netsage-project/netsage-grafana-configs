#!/usr/bin/env bash
set -e 


cd /vagrant/templates/
pip3 install -r requirements.txt
echo "Updating Grafana Config"
./apply_templates.py --type GRAFANA_CONFIG && cp -f grafana.ini /etc/grafana/grafana.ini
echo "Updating Menu Items"
./apply_templates.py --type MENUS
echo "Updating Footer on Dashboards"
./apply_templates.py --type FOOTER_UPDATES
echo "Updating Query on Dashboards"
./apply_templates.py --type QUERY_OVERRIDE
echo "Updating Google Analytics on Dashboards"
./apply_templates.py --type GOOGLE_ANALYTICS


#Install wizzy
cd /vagrant
npm install -g wizzy@0.6.0

### Start plugin installs ###
cd /vagrant/plugins

#install carpetplot
grafana-cli plugins install petrslavotinek-carpetplot-panel

## BEGIN PLUGIN INSTALL ##

#install tsds datasource plugin
cd tsds-grafana
npm install -g yarn #make seems to need this
make rpm
alien -i $HOME/rpmbuild/RPMS/noarch/globalnoc-tsds-datasource-*.noarch.rpm
mv /usr/com/grafana/plugins/globalnoc-tsds-datasource/ /var/lib/grafana/plugins/
cd ../


#Install network panel plugin
cd globalnoc-networkmap-panel
npm install -g gulp #make seems to need this
make rpm
alien -i $HOME/rpmbuild/RPMS/noarch/grnoc-grafana-worldview-*.noarch.rpm
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

#Install navigation
# HACK: for some reason this fails to install unless it's moved to a different location.
cp -r  Netsage-Slope_graph /tmp/
pushd . 
cd /tmp/Netsage-Slope_graph/
make install
popd
### End plugin source code installs ###



## END PLUGIN INSTALL ##