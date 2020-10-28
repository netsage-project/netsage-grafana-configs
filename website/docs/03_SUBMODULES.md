---
id: plugin_submodules
title: Plugin Submodules
sidebar_label: Submodules
---
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

