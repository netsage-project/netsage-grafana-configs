import logging
import json
import re

from abc import ABC, abstractmethod

from jinja2 import Template

from .support_types import ExecutionType
from os.path import isfile, join, realpath, dirname
from os import listdir
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class AbstractTemplateProcessor(ABC):
    """
    defines an abstract class with some helper functionality
    inherited by specialized TemplateProcessors
    """

    def __init__(self, execution_type: ExecutionType, config: dict):
        key = str(execution_type).lower()
        self.type = execution_type
        self.__config__ = config
        self.__common__ = config.get('common', {})
        self.__namespace__ = key

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def is_valid(self, panel):
        pass

    def safe_dashboard(self, dashboard, data):
        with open(dashboard, 'w') as outfile:
            json.dump(data, outfile, indent=2, sort_keys=True)

    def __get_wizzy_dashboards__(self):
        """
        :return: List of strings representing the path of all dashboards
        """
        dashboard_path = realpath(join(dirname(__file__), '..', '..', self.get_value('dashboard_location', 'common')))
        dashboard_list = [join(dashboard_path, f) for f in listdir(dashboard_path) if isfile(join(dashboard_path, f))]
        return dashboard_list

    def get_value(self, key, ns):
        """
        :param key:  the config value
        :param ns: the namespace we're reading from
        :return: The value if one exists
        """
        return self.__config__.get(ns, {}).get(key, None)


class TemplateGrafanaProcessor(AbstractTemplateProcessor):
    """
    Used to generate a customize grafana.ini config
    """

    def __init__(self, config: dict):
        super().__init__(ExecutionType.GRAFANA_CONFIG, config)

    def process(self):
        """
        Uses the speicified template file and inject values for the define named space and outputs it at the location
        specified
        :return:
        """
        try:
            f = open(self.get_value('input_file', self.__namespace__), 'r')
            raw_template = f.read()
        except FileNotFoundError as e:
            log.error("Failed to read template file.  Cannot process Grafana config.", )
            return
        tmp = Template(raw_template)
        result = tmp.render(self.__config__.get(self.__namespace__, {}))

        file_name = self.get_value('output_file', self.__namespace__)
        if result is not None:
            f = open(file_name, 'w')
            f.write(result)
            f.close()
            log.info("Rendered grafana config as {}".format(file_name))
        else:
            log.error("Failed to create grafana config as {}".format(file_name))

    def is_valid(self, panel):
        pass


class TemplateMenuProcessor(AbstractTemplateProcessor):

    def __init__(self, config: dict):
        super().__init__(ExecutionType.MENUS, config)

    def process(self):
        """
        Updates the navigation Menu on all dashboards with the values specified in the config yaml file
        """
        log.info("Executing for type: {} my ins type is: {}".format(self.type, str(type(self))))
        dashboard_list = self.__get_wizzy_dashboards__()
        for dashboard in dashboard_list:
            self.__apply_dashboard_changes__(dashboard)

    def __apply_dashboard_changes__(self, dashboard):
        """
        Identifies the Menu section in the dashboard if one exists it will get updated,
        otherwise it's a NoOp
        """
        log.info("Processing dashboard {}".format(dashboard))
        menu_panel = None
        with open(dashboard, 'r', encoding='utf-8') as file:
            data = json.load(file)
        panels = data.get('panels', [])
        for panel in panels:
            if self.is_valid(panel):
                menu_panel = panel
                break
        if menu_panel is None:
            log.warning("No Menu detected for dashboard: {}".format(dashboard))
            return

        menu_panel['array_option_1'] = self.get_value('menu_text', ns='menus')
        menu_panel['array_option_2'] = self.get_value('menu_values', ns='menus')

        log.info("Updating dashboard: {}".format(dashboard))
        self.safe_dashboard(dashboard, data)

    def is_valid(self, panel):
        return '__netsage_template' in panel


class TemplateFooterProcessor(AbstractTemplateProcessor):
    """
    This Processor is responsible for updating / replacing the footer on each dashboard, if it contains a footer/html
    panel.
    """

    def __init__(self, config: dict):
        super().__init__(ExecutionType.FOOTER_UPDATES, config)

    def process(self):
        """
        Replace the footer on each dashboard
        """
        dashboard_list = self.__get_wizzy_dashboards__()
        for dashboard in dashboard_list:
            self.__apply_dashboard_changes__(dashboard)

    def __apply_dashboard_changes__(self, dashboard):
        """
        updates footer on the dashboard file if it contains a valid entry
        """
        log.info("Processing dashboard {} for type: {}".format(dashboard, self.type))
        with open(dashboard, 'r') as file:
            data = json.load(file)
        panels = data.get('panels', [])
        panel = panels[len(panels) - 1]  # get footer panel

        if self.is_valid(panel):
            log.error("Last panel is not in HTML mode or of type text, invalid footer panel detected")

        panel['content'] = self.get_value('template', self.__namespace__)

        log.info("Updating dashboard: {} with new footer".format(dashboard))
        self.safe_dashboard(dashboard, data)

    def is_valid(self, panel):
        """
        Ensures that the panel is a valid footer panel
        """
        return panel['mode'] != 'html' or panel['type'] != 'text'


class TemplateQueryOverride(AbstractTemplateProcessor):
    """
    This Processor is responsible for updating certain queries as defined by the template config.

    It will process every pair of (name, value) and apply the changes to the template if any are found.
    """

    def __init__(self, config: dict):
        super().__init__(ExecutionType.QUERY_OVERRIDE, config)

    def process(self):
        """
        Replace the query on each dashboard
        """
        dashboard_list = self.__get_wizzy_dashboards__()
        for dashboard in dashboard_list:
            self.__apply_dashboard_changes__(dashboard)

    def __apply_dashboard_changes__(self, dashboard):
        """
        Note this method isn't especially optimal.  If the number of variable and number of dashboards grows very
        large this needs to be revisited.  O(num of dashboards * num of changes)
        :param dashboard:
        :return:
        """
        log.info("Processing dashboard {} for type: {}".format(os.path.basename(dashboard), self.type))
        with open(dashboard, 'r') as file:
            data = json.load(file)
        panels = data.get('templating', []).get('list', [])
        for panel in panels:
            if self.is_valid(panel):
                name = panel.get('name')
                for request in self.__config__[self.__namespace__]:
                    key = request.get('name', '')
                    request_value = request.get('value', '')
                    if name == key:
                        panel['query'] = request_value if len(request_value) > 0 else panel['query']
                        log.debug("updated query on dashboard: {} for variable: {} with value: {}".format(
                            os.path.basename(dashboard), key, request_value))

        self.safe_dashboard(dashboard, data)

    def is_valid(self, panel):
        """
        Ensure both name and query must be present
        """
        return 'name' in panel and 'query' in panel


class TemplateAnalyticsOverride(AbstractTemplateProcessor):
    """
    This Processor is responsible for updating The Google Analytics ID in any content tag for any match found

    """

    def __init__(self, config: dict):
        super().__init__(ExecutionType.GOOGLE_ANALYTICS, config)
        self.pattern = re.compile(".*UA-\d+-\d.*")

    def process(self):
        """
        Replace the query on each dashboard
        """
        dashboard_list = self.__get_wizzy_dashboards__()
        for dashboard in dashboard_list:
            self.__apply_dashboard_changes__(dashboard)

    def __apply_dashboard_changes__(self, dashboard):
        """
        Updates google ID wherever it's been found.
        
        :param dashboard:
        :return:
        """
        log.info("Processing dashboard {} for type: {}".format(os.path.basename(dashboard), self.type))
        with open(dashboard, 'r') as file:
            data = json.load(file)
        panels = data.get('panels', [])
        content_key = 'content'
        for panel in panels:
            google_key = self.get_value('id', self.__namespace__)
            if self.is_valid(panel):
                content = panel.get(content_key)
                content = re.sub(r"UA-\d+-\d", google_key, content)
                panel[content_key] = content

        self.safe_dashboard(dashboard, data)

    def is_valid(self, panel):
        """
        Ensure Google Analytics ID is found in the content section
        """
        if 'content' not in panel:
            return False
        content = panel.get('content')
        # Ensure Analytics ID is present
        match = self.pattern.search(content)
        return match is not None
