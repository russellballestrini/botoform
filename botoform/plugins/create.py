from botoform.builders import EnvironmentBuilder

from botoform.config import ConfigLoader

from botoform.util import key_value_to_dict

from argparse import SUPPRESS

class Create(object):
    """Create a new VPC and related services, modeled from YAML template."""

    @staticmethod
    def setup_parser(parser):
        parser.add_argument('--skip-evpc', default=True, help=SUPPRESS)
        parser.add_argument('cidrblock',
          help='The CIDR block to use when creating VPC.')
        parser.add_argument('config',
          help='The botoform YAML config template.')
        parser.add_argument('-v', '--vars',
          default=list(), action='append', metavar='key=val',
          help='Jinja2 context: --vars key=val,key2=val2,key3=val3'
        )
        parser.add_argument('-t', '--tags',
          default=list(), action='append', metavar='key=val',
          help='AWS resource: --tags key=val,key2=val2,key3=val3'
        )

    @staticmethod
    def main(args, evpc):
        """Output a list of instance names. (example botoform plugin)"""
        context_vars = key_value_to_dict(args.vars)
        aws_tags = key_value_to_dict(args.tags)
        loader = ConfigLoader(template_dir='tests', context_vars = context_vars)
        config = loader.load(template_file = args.config)
        ebuilder = EnvironmentBuilder(
                       args.vpc_name, config, args.region, args.profile)
        ebuilder.build_vpc(args.cidrblock)
        ebuilder.apply_all()


