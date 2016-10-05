from botoform.util import output_formatter

from botoform.builders import EnvironmentBuilder

from botoform.config import ConfigLoader

def get_builder_for_existing_vpc(evpc, config_path):
    loader = ConfigLoader(context_vars={'vpc_name' : evpc.name, 'vpc_cidr' : evpc.cidr_block})
    config = loader.load(config_path)
    builder = EnvironmentBuilder(evpc.name, config, evpc.boto.region_name, evpc.boto.profile_name)
    builder.evpc = evpc
    return builder

def ec2_tags(args, evpc):
    """
    Refresh private zone with new records / values.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args.config)
    builder.finish_instance_roles(builder.config['instance_roles'])

def private_zone(args, evpc):
    """
    Refresh private zone with new records / values.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args.config)
    builder.finish_instance_roles(builder.config['instance_roles'])
    evpc.route53.refresh_private_zone()

refresh_subcommands = {
  'ec2_tags'     : ec2_tags,
  'private_zone' : private_zone,
}

class Refresh(object):
    """
    Refresh AWS resource.

    This is a :ref:`class plugin` for the :ref:`bf` tool.
    """

    @staticmethod
    def setup_parser(parser):
        parser.add_argument('refresh_subcommand', choices=refresh_subcommands)
        parser.add_argument('config',
          help='The botoform YAML config template.')
        #parser.add_argument('-e', '--extra-vars',
        #  default=list(), action='append', metavar='key=val',
        #  help='Extra Jinja2 context: --extra-vars key=val,key2=val2,key3=val3'
        #)

    @staticmethod
    def main(args, evpc):
        refresh_subcommands[args.refresh_subcommand](args, evpc)


