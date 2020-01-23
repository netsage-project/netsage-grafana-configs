from enum import Enum


class ExecutionType(Enum):
    """
    Enum defined which type of execution is being processed.

    Please note the enum name is the title of the top level of for the configuration
    in the yaml file.

    ie. all the config relating to menu changes will be under menus:
    """
    GRAFANA_CONFIG = 1,
    MENUS = 2,
    FOOTER_UPDATES = 3

    def __str__(self):
        return self.name
