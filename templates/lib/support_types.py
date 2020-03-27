from enum import Enum


class ExecutionType(Enum):
    """
    Enum defined which type of execution is being processed.

    Please note the enum name is the title of the top level of for the configuration
    in the yaml file.

    ie. all the config relating to menu changes will be under menus:
    """
    ALL = 0
    GRAFANA_CONFIG = 1
    MENUS = 2
    FOOTER_UPDATES = 3
    QUERY_OVERRIDE = 4
    GOOGLE_ANALYTICS = 5
    DISABLE_PANEL = 6

    def __str__(self):
        return self.name
