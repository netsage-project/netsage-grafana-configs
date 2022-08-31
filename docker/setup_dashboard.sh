#!/usr/bin/env bash
set -e

cd /app/templates/
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
cd /app
npm install -g wizzy

### Start plugin installs ###
cd /app/plugins

## BEGIN PLUGIN INSTALL ##

#Install carpetplot 
grafana-cli plugins install marcusolsson-hourly-heatmap-panel
#grafana-cli --pluginUrl "https://github.com/katrinaturner/grafana-hourly-heatmap-panel/archive/nullColorPickerTest.zip" plugins install marcusolsson-hourly-heatmap-panel

# Install polystat
grafana-cli plugins install grafana-polystat-panel

#Install tsds datasource plugin
cd tsds-grafana
npm install -g yarn #make seems to need this
# yarn install
# yarn build
make rpm
alien -i $HOME/rpmbuild/RPMS/noarch/globalnoc-tsds-datasource-*.noarch.rpm
mv /usr/com/grafana/plugins/globalnoc-tsds-datasource/ /var/lib/grafana/plugins/
cd ../

# Install worldview panel plugin
cd globalnoc-worldview-panel
yarn install
yarn build
mv /app/plugins/globalnoc-worldview-panel/ /var/lib/grafana/plugins/
cd ../

#Install netsage-sankey plugin
cd netsage-sankey-plugin
yarn install
yarn build
mv /app/plugins/netsage-sankey-plugin/ /var/lib/grafana/plugins/
cd ../

#Install navigation
cd netsage-nav-plugin
yarn install
yarn build
mv /app/plugins/netsage-nav-plugin/ /var/lib/grafana/plugins/
cd ..

#Install discipline map plugin
cd science-discipline-map-plugin/
yarn install
yarn build
mv /app/plugins/science-discipline-map-plugin/ /var/lib/grafana/plugins/
cd ..

#Install slope graph plugin
cd netsage-slopegraph-panel/
yarn install
yarn build
mv /app/plugins/netsage-slopegraph-panel/ /var/lib/grafana/plugins/
cd ..

#Install bump chart plugin
cd netsage-bumpchart-panel/
yarn install
yarn build
mv /app/plugins/netsage-bumpchart-panel/ /var/lib/grafana/plugins/
cd ..

### End plugin source code installs ###

### End plugin source code installs ###

## END PLUGIN INSTALL ##
