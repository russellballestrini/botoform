import yaml
from jinja2 import (
  Environment,
  FileSystemLoader,
  Template,
)

#from util import get_port_range

class BFConfigLoader:
    def __init__(self, template_dir="templates", context_vars=None):
        self.jinja2_env = Environment(loader=FileSystemLoader(template_dir))
        self.context_vars = context_vars if context_vars is not None else {}

    def _render_template(self, template):
        return template.render(self.context_vars)

    def render(self, template_file):
        """Return Jinja2 render of template file with context_vars."""
        return self._render_template(self.jinja2_env.get_template(template_file))

    def render_string(self, template_string):
        """Return Jinja2 render of template_str with context_vars."""
        return self._render_template(Template(template_string))

    def _load(self, template_file, template_string):
        if template_file is None and template_string is None:
            raise Exception('missing template template_file or template_string')
        if template_string:
            rendered = self.render_string(template_string)
        if template_file:
            rendered = self.render(template_file)
        return yaml.load(rendered)

    def _remove_excluded_roles(self, config, exclude_roles):
        """remove excluded roles and security groups from config"""
        exclude_roles = exclude_roles if exclude_roles is not None else []
        for role in exclude_roles:

            # remove excluded service_role sg references.
            for key, value in config['instance_roles'].items():
                if role in value['security_groups']:
                    config['instances'][key]['security_groups'].remove(role)

            # remove excluded instance roles.
            if role in config.get('instances', {}):
                del config['instances'][role]

            # remove excluded security_groups.
            if role in config.get('security_groups', {}):
                del config['security_groups'][role]

            # remove excluded security_group rule references.
            for sg_name, sg_rules in config['security_groups'].items():
                clean_rules = []
                for rule in sg_rules:
                    if rule[0] != role:
                        clean_rules.append(rule)
                config['security_groups'][sg_name] = clean_rules

        return config

    def _mutate_port_ranges(self, config):
        """mutate security group port ranges into desired schema"""
        # rule[0] = source, rule[1] = protocol, rule[2] = raw range
        for sg_name, rules in config.get('security_groups', {}).items():
            for rule in rules:
                # mutate rule port range into (from_port, to_port) tuple.
                rule[2] = get_port_range(rule[2], rule[1])
        return config

    def load(self, template_file=None, template_string=None, exclude_roles=None):
        """
        Use Jinja2 to render template with context_vars,
        return Python representation of JSON config.
        """
        config = self._load(template_file, template_string)
        #config = self._remove_excluded_roles(config, exclude_roles)
        #config = self._mutate_port_ranges(config)
        return config
