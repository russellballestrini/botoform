from os import path
import yaml
from jinja2 import (
  Environment,
  FileSystemLoader,
  Template,
)

#from util import get_port_range

class ConfigLoader(object):
    def __init__(self, template_dir=None, context_vars=None):
        self.jinja2_env = None
        self._template_dir = None
        self.context_vars = context_vars if context_vars is not None else {}
        if template_dir is not None:
            self.template_dir = template_dir

    @property
    def template_dir(self):
        return self._template_dir

    @template_dir.setter
    def template_dir(self, new_template_dir):
        self.jinja2_env = Environment(loader=FileSystemLoader(new_template_dir))
        self._template_dir = new_template_dir

    def _render_template(self, template):
        return template.render(self.context_vars)

    def render(self, template_file):
        """Return Jinja2 render of template with context_vars."""
        return self._render_template(self.jinja2_env.get_template(template_file))

    def render_string(self, template_string):
        """Return Jinja2 render of template_str with context_vars."""
        return self._render_template(Template(template_string))

    def _load(self, template_path=None, template_string=None):
        if template_path is None and template_string is None:
            raise Exception('missing template template_path or template_string')
        if template_string:
            rendered = self.render_string(template_string)
        if template_path:
            if self.jinja2_env is None:
                self.template_dir = path.dirname(template_path)
                template_file = path.basename(template_path)
            else:
                template_file = template_path
            rendered = self.render(template_file)
        return yaml.load(rendered)

    def _load_includes(self, config):
        """Load YAML path includes and return config. Will clobber existing."""
        for key, path in config['includes'].items():
            config[key] = self._load(template_path=path)[key]
        return config

    def _mutate_port_ranges(self, config):
        """mutate security group port ranges into desired schema"""
        # rule[0] = source, rule[1] = protocol, rule[2] = raw range
        for sg_name, rules in config.get('security_groups', {}).items():
            for rule in rules:
                # mutate rule port range into (from_port, to_port) tuple.
                rule[2] = get_port_range(rule[2], rule[1])
        return config

    def load(self, template_path=None, template_string=None):
        """
        Use Jinja2 to render template with context_vars,
        return Python representation of YAML config.
        """
        config = self._load(template_path, template_string)
        config = self._load_includes(config)
        #config = self._mutate_port_ranges(config)
        return config
