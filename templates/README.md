# Template Processor

Install the python requirements defined in requirements.txt either using pip or pipenv.

```shell script
pip install -r requirements.txt
```

```shell script
pipenv install -r requirements.txt
```

## Execute script

```sh
./apply_template.py -h 
 ```

```shell script
Template Processor

optional arguments:
  -h, --help            show this help message and exit
  --type {GRAFANA_CONFIG,MENUS,FOOTER_UPDATES} Type of template
```


For example if you wish to update the menus and reflect the changes on the dashboard

1. update template_values.yaml
2. Run the script
3. wizzy export dashboards

###Note:

As a convenience you can also run:

```sh
./apply_template.py --type ALL
 ```

This will execution every configure processor on the dashboards.
