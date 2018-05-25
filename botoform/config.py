from os import path
import yaml
from jinja2 import Environment, FileSystemLoader, Template


class ConfigLoader(object):
    """
    Loads :ref:`Botoform Schema <schema reference>` and returns a dictionary.
    """

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
            raise Exception("missing template template_path or template_string")
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
        for key, paths in config.get("includes", {}).items():
            if key not in config:
                config[key] = {}
            if not isinstance(paths, list):
                # convert a single path string into a list.
                paths = [paths]
            for path in paths:
                config[key].update(self._load(template_path=path)[key])
        return config

    def _sg_rule_tuples(self, config):
        """change security group rules to be tuples instead of lists."""
        sg_config = config.get("security_groups", {})
        _sg_config = config.get("security_groups", {})
        for sg_name, values in sg_config.items():
            if "inbound" in values:
                rules = sg_config[sg_name]["inbound"]
                _sg_config[sg_name]["inbound"] = [tuple(rule) for rule in rules]
            if "outbound" in values:
                rules = sg_config[sg_name]["outbound"]
                _sg_config[sg_name]["outbound"] = [tuple(rule) for rule in rules]
        config["security_groups"] = _sg_config
        return config

    def load(self, template_path=None, template_string=None):
        """
        Load a :ref:`Botoform Schema <schema reference>` config and render with Jinja2.

        :param template_path: Path to the config to load and render.
        :param template_string: String to load and render. Optional.

        :returns: 
          Python dictionary representation of :ref:`config <schema reference>`.
        """
        config = self._load(template_path, template_string)
        config = self._load_includes(config)
        config = self._sg_rule_tuples(config)
        return config
