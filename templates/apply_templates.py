#!/usr/bin/env python3
import os
import sys

import logging
import yaml
import argparse
from lib.processor import TemplateGrafanaProcessor, TemplateMenuProcessor, TemplateFooterProcessor, TemplateQueryOverride, TemplateAnalyticsOverride
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
                        ExecutionType.GOOGLE_ANALYTICS: TemplateAnalyticsOverride(self.__config__)
                        }

    def process(self, execution_type):
        """
        Will process the request if a valid one is defined.
        """
        if execution_type == ExecutionType.ALL:
            for enum_type in self.callers:
                reference = self.callers.get(enum_type)

                if reference is not None:
                    reference.process()
            return

        reference = self.callers.get(execution_type, None)

        if reference is None:
            log.error("Cannot proceed.  Type: {} has no configured processor".format(type))
            return

        reference.process()


def parse_arguments():
    """
    CLI parser
    :return:  parsed arguments
    """
    parser = argparse.ArgumentParser(description='Template Processor')

    parser.add_argument('--type', type=lambda mtype: ExecutionType[mtype], choices=list(ExecutionType),
                        help='Type of template', default=ExecutionType.GRAFANA_CONFIG)

    try:
        args = parser.parse_args()
        return args
    except:
        log.error("invalid parameters, please check config and try again")
        parser.print_help()
        sys.exit(1)


def main():
    args = parse_arguments()
    runner = Runner()
    runner.process(args.type)


if __name__ == '__main__':
    main()
