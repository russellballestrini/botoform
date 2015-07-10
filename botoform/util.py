import yaml
import json

class BotoformDumper(yaml.Dumper):
    """A custom YAML dumper that is pretty."""
    def increase_indent(self, flow=False, indentless=False):
        return super(BotoformDumper, self).increase_indent(flow, False)

def output_formatter(data, output_format='newline'):
    """Print data in the optional output_format."""
    if output_format.lower() == 'newline':
        output = '\n'.join(data)
    elif output_format.upper() == 'CSV':
        output = ', '.join(data)
    elif output_format.upper() == 'YAML':
        output = yaml.dump(data, Dumper=BotoformDumper)
    elif output_format.upper() == 'JSON':
        output = json.dumps(data, indent=2)
    return output

def reflect_attrs(child, parent):
    """Composition Magic: reflect all missing parents attributes into child."""
    existing = dir(child)
    for attr in dir(parent):
        if attr not in existing:
            child.__dict__[attr] = getattr(parent, attr)

