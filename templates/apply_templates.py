#!/usr/bin/env python3
import json
import os
import sys

import logging
from os.path import realpath, join, dirname, isfile

import yaml
import argparse
from lib.processor import *
from lib.support_types import ExecutionType

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class Runner(object):
    """
        Loads the config and defines all possible execution paths.
    """

    def __init__(self, config='template_values.yaml'):
        with open(config, 'r') as file:
            self.__config__ = yaml.full_load(file)

        self.callers = {ExecutionType.MENUS: TemplateMenuProcessor(self.__config__),
                        ExecutionType.GRAFANA_CONFIG: TemplateGrafanaProcessor(self.__config__),
                        ExecutionType.FOOTER_UPDATES: TemplateFooterProcessor(self.__config__),
                        ExecutionType.QUERY_OVERRIDE: TemplateQueryOverride(self.__config__),
                        ExecutionType.GOOGLE_ANALYTICS: TemplateAnalyticsOverride(self.__config__),
                        ExecutionType.DISABLE_PANEL: DisableDashboardPanels(self.__config__)
                        }

    def process(self, execution_type):
        """
        Will process the request if a valid one is defined.
        """
        references = []

        if execution_type is None or (self.callers.get(execution_type) is None and execution_type != ExecutionType.ALL):
            log.error("Cannot proceed.  Type: {} has no configured processor".format(type))
            return

        # Handle the ALL use case
        if execution_type == ExecutionType.ALL:
            for enum_type in self.callers:
                if self.is_dashboard(enum_type):
                    references.append(enum_type)
                else:
                    self.process_reference(enum_type)

        # Handle the individual request use case
        else:
            if self.is_dashboard(execution_type):
                references = [execution_type]
            else:
                self.process_reference(execution_type)

        if len(references) > 0:
            dashboards = self.__get_wizzy_dashboards__()
            for dashboard in dashboards:
                data = None
                with open(dashboard, 'r', encoding='utf-8') as file:
                    data = file.read()
                    data = json.loads(data)
                for enum_type in references:
                    data = self.process_reference(enum_type, dashboard, data)

                self.save_dashboard(dashboard, data)

    def save_dashboard(self, dashboard, data):
        with open(dashboard, 'w') as outfile:
            json.dump(data, outfile, indent=2, sort_keys=True)

    def process_reference(self, enum_type, dashboard=None, data=None):
        reference = self.callers.get(enum_type)
        if reference is None:
            log.error("Cannot proceed.  Type: {} has no configured processor".format(type))
            return data
        return reference.process(dashboard, data)

    def is_dashboard(self, enum, key='updates_dashboards'):
        ns = str(enum).lower()
        return self.__config__.get(ns, {}).get(key, False)

    def __get_wizzy_dashboards__(self):
        """
        :return: List of strings representing the path of all dashboards
        """
        dashboard_path = realpath(
            join(dirname(__file__), '..', self.__config__.get('common', {}).get('dashboard_location', None)))
        dashboard_list = [join(dashboard_path, f) for f in os.listdir(dashboard_path) if
                          isfile(join(dashboard_path, f))]
        return dashboard_list


def parse_arguments():
    """
    CLI parser
    :return:  parsed arguments
    """
    parser = argparse.ArgumentParser(description='Template Processor')

    parser.add_argument('-t', '--type', type=lambda mtype: ExecutionType[mtype], choices=list(ExecutionType),
                        help='Type of template', default=ExecutionType.GRAFANA_CONFIG)
    parser.add_argument('-f', '--config', type=str,
                        help='location of config file', default='template_values.yaml')

    try:
        args = parser.parse_args()
        return args
    except:
        log.error("invalid parameters, please check config and try again")
        parser.print_help()
        sys.exit(1)


def main():
    args = parse_arguments()
    runner = Runner(args.config)
    runner.process(args.type)


if __name__ == '__main__':
    main()
