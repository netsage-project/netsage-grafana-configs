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