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
    def process(self, dashboard, json_data=None):
        pass

    @abstractmethod
    def is_valid(self, panel):
        pass

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

    def process(self, dashboard, raw_data=None):
        """
        Uses the specified template file and inject values for the define named space and outputs it at the location
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

    def process(self, dashboard, data=None):
        """
        Updates the navigation Menu on all dashboards with the values specified in the config yaml file
        """
        log.info("Processing dashboard {}".format(dashboard))
        menu_panel = None

        panels = data.get('panels', [])
        for panel in panels:
            if self.is_valid(panel):
                menu_panel = panel
                break
        if menu_panel is None:
            log.warning("No Menu detected for dashboard: {}".format(dashboard))
            return

        menu_panel['link_text'] = self.get_value('menu_text', ns='menus')
        menu_panel['link_url']  = self.get_value('menu_values', ns='menus')

        log.info("Updating dashboard: {}".format(dashboard))
        return data

    def is_valid(self, panel):
        return '__netsage_template' in panel


class TemplateFooterProcessor(AbstractTemplateProcessor):
    """
    This Processor is responsible for updating / replacing the footer on each dashboard, if it contains a footer/html
    panel.
    """

    def __init__(self, config: dict):
        super().__init__(ExecutionType.FOOTER_UPDATES, config)

    def process(self, dashboard, data=None):
        """
        Replace the footer on each dashboard
        """
        log.info("Processing dashboard {} for type: {}".format(dashboard, self.type))
        panels = data.get('panels', [])
        panel = panels[len(panels) - 1]  # get footer panel

        if self.is_valid(panel):
            log.error("Last panel is not in HTML mode or of type text, invalid footer panel detected")

        panel['content'] = self.get_value('template', self.__namespace__)

        log.info("Updating dashboard: {} with new footer".format(dashboard))
        return data

    def is_valid(self, panel):
        """
        Ensures that the panel is a valid footer panel
        """
        html_check = False 
        text_check = False
        if 'mode' in panel:
            html_check = panel['mode'] != 'html'
        if 'type' in panel:
            text_check = panel['type'] != 'text'
    
        return html_check or text_check


class TemplateQueryOverride(AbstractTemplateProcessor):
    """
    This Processor is responsible for updating certain queries as defined by the template config.

    It will process every pair of (name, value) and apply the changes to the template if any are found.
    """

    def __init__(self, config: dict):
        super().__init__(ExecutionType.QUERY_OVERRIDE, config)

    def process(self, dashboard, data=None):
        """
        Replace the query on each dashboard

        Note this method isn't especially optimal.  If the number of variable and number of dashboards grows very
        large this needs to be revisited.  O(num of dashboards * num of changes)
        :param dashboard:
        :return:
        """
        log.info("Processing dashboard {} for type: {}".format(os.path.basename(dashboard), self.type))
        panels = data.get('templating', []).get('list', [])
        for panel in panels:
            if self.is_valid(panel):
                name = panel.get('name')
                for request in self.__config__.get(self.__namespace__, {}).get('data', {}):
                    key = request.get('name', '')
                    request_value = request.get('value', '')
                    if name == key:
                        panel['query'] = request_value if len(request_value) > 0 else panel['query']
                        log.debug("updated query on dashboard: {} for variable: {} with value: {}".format(
                            os.path.basename(dashboard), key, request_value))

        return data

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

    def process(self, dashboard, data=None):
        """
        Replace the query on each dashboard

        Updates google ID wherever it's been found.
        
        :param dashboard:
        :return:
        """
        log.info("Processing dashboard {} for type: {}".format(os.path.basename(dashboard), self.type))
        panels = data.get('panels', [])
        content_key = 'content'
        for panel in panels:
            google_key = self.get_value('id', self.__namespace__)
            if self.is_valid(panel):
                content = panel.get(content_key)
                content = re.sub(r"UA-\d+-\d", google_key, content)
                panel[content_key] = content

        return data

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


class DisableDashboardPanels(AbstractTemplateProcessor):
    """
    This Processor is responsible for Disabling certain panels on a specific dashboard.

    For each dashboard specified it will match based on the id or title and disable any panels that match
    any of the specified fields

    """

    def __init__(self, config: dict):
        super().__init__(ExecutionType.DISABLE_PANEL, config)
        self.__panels__ = self.__config__.get('disable_panel', {}).get('data', [])
        self.valid_dashboards = set([t.get('dashboard_name', '') for t in self.__panels__])
        self.id_mappings = {k.get('dashboard_name'): k.get('panel_ids') for (k) in self.__panels__}
        self.title_mappings = {k.get('dashboard_name'): k.get('titles', []) for (k) in self.__panels__}

    def process(self, dashboard, data=None):
        """
        Replace the query on each dashboard
        """
        dashboard_name = os.path.basename(dashboard)
        if dashboard_name in self.valid_dashboards:
            return self.__apply_dashboard_changes__(dashboard_name, data)
        else:
            return data

    def __apply_dashboard_changes__(self, dashboard, data):
        """
        Updates google ID wherever it's been found.

        :param dashboard:
        :return:
        """
        log.info("Processing dashboard {} for type: {}".format(os.path.basename(dashboard), self.type))
        panels = data.get('panels', [])
        id_panels_to_disable = set(self.id_mappings.get(dashboard, []))
        title_panels_to_disable = set(self.title_mappings.get(dashboard, []))
        removal_list = []
        for panel in panels:
            remove_panel = False
            if panel.get('id', -1) in id_panels_to_disable:
                remove_panel = True
            if panel.get('title') in title_panels_to_disable:
                remove_panel = True
            if remove_panel:
                removal_list.append(panel)

        for item in removal_list:
            panels.remove(item)

        return data

    def is_valid(self, panel):
        """
        Ensure Google Analytics ID is found in the content section
        """
        True


class DefaultOverrideTemplate(AbstractTemplateProcessor):
    """
    This Processor is responsible for Disabling certain panels on a specific dashboard.

    For each dashboard specified it will match based on the id or title and disable any panels that match
    any of the specified fields

    """

    def __init__(self, config: dict):
        super().__init__(ExecutionType.DEFAULT_OVERRIDE, config)
        self.__panels__ = self.__config__.get('default_override', {}).get('data', [])
        self.valid_dashboards = set([t.get('dashboard_name', '') for t in self.__panels__])
        self.mappings = {k.get('dashboard_name'): k for (k) in self.__panels__}

    def process(self, dashboard, data=None):
        """
        Replace the query on each dashboard
        """
        dashboard_name = os.path.basename(dashboard)
        if dashboard_name in self.valid_dashboards:
            return self.__apply_dashboard_changes__(dashboard_name, data)
        else:
            return data

    def __apply_dashboard_changes__(self, dashboard, data):
        """
        Updates google ID wherever it's been found.

        :param dashboard:
        :return:
        """
        log.info("Processing dashboard {} for type: {}".format(os.path.basename(dashboard), self.type))
        templates = data.get('templating', {}).get('list')
        template_request = self.mappings.get(dashboard, [])
        for panel in templates:
            if panel.get('name') == template_request.get('name'):
                panel_defaults = panel.get('current', {})
                panel_defaults['text'] = template_request.get('text')
                panel_defaults['value'] = template_request.get('value')
                break

        return data

    def is_valid(self, panel):
        """
        Ensure Google Analytics ID is found in the content section
        """
        True
