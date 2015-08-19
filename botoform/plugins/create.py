from botoform.builders import EnvironmentBuilder

from botoform.config import ConfigLoader

from botoform.util import key_value_to_dict

class Create(object):
    """Output a list of instance names. (example botoform plugin)"""

    @staticmethod
    def setup_parser(parser):
        parser.add_argument('--skip-evpc', default=True, help='==SUPPRESS==')
        parser.add_argument('config',
          help='The botoform YAML config template.')
        parser.add_argument('-v', '--vars',
          default=list(), action='append',
          help='Jinja2 vars: -v key=val,key2=val2 or -v key1=val -v key2=val2'
        )
        parser.add_argument('-t', '--tags',
          default=list(), action='append',
          help='AWS Tags: -t key=val,key2=val2 or -t key1=val -t key2=val2'
        )

    @staticmethod
    def main(args, evpc):
        """Output a list of instance names. (example botoform plugin)"""
        context_vars = key_value_to_dict(args.vars)
        aws_tags = key_value_to_dict(args.tags)
        loader = ConfigLoader(template_dir='tests', context_vars = context_vars)
        config = loader.load(template_file = args.config)
        ebuilder = EnvironmentBuilder(config, args.region, args.profile)
        ebuilder.build()


