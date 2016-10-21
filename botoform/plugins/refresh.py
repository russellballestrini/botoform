from botoform.util import output_formatter

from botoform.builders import EnvironmentBuilder

from botoform.config import ConfigLoader

from collections import defaultdict

def get_builder_for_existing_vpc(evpc, config_path):
    loader = ConfigLoader(context_vars={'vpc_name' : evpc.name, 'vpc_cidr' : evpc.cidr_block})
    config = loader.load(config_path)
    builder = EnvironmentBuilder(evpc.name, config, evpc.boto.region_name, evpc.boto.profile_name)
    builder.evpc = evpc
    builder.amis = config['amis']
    return builder

def ec2_tags(args, evpc):
    """
    Refresh ec2 instances and volumes with tags.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args.config)
    builder.finish_instance_roles(builder.config['instance_roles'])

def instance_roles(args, evpc):
    """
    Refresh ec2 instances and volumes with tags.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args.config)
    builder.instance_roles(builder.config['instance_roles'])
    builder.wait_for_instance_roles_to_exist(builder.config['instance_roles'])
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
    evpc.route53.create_private_zone()
    evpc.route53.refresh_private_zone()

def security_groups(args, evpc):
    """
    Refresh security_groups: add missing groups and rules.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args.config)
    builder.security_groups(builder.config.get('security_groups', {}))

    security_groups_config  = builder.config.get('security_groups', {})
    security_groups_current = evpc.enriched_security_groups
    
    rules_to_add = defaultdict(dict)
    rules_to_del = defaultdict(dict)

    for sg_name in security_groups_config:
        config  = security_groups_config[sg_name]
        current = security_groups_current[sg_name]
        
        to_add_inbound  = set(config.get('inbound', [])) - set(current.get('inbound',[]))
        to_add_outbound = set(config.get('outbound', [])) - set(current.get('outbound',[]))

        #to_remove_inbound  = set(current.get('inbound', [])) - set(config.get('inbound',[]))
        #to_remove_outbound = set(current.get('outbound', [])) - set(config.get('outbound',[]))

        if len(to_add_inbound) != 0:
            rules_to_add[sg_name]['inbound'] = list(to_add_inbound)
        if len(to_add_outbound) != 0:
            rules_to_add[sg_name]['outbound'] = list(to_add_outbound)

    #print rules_to_del

    builder.security_group_rules(rules_to_add)

refresh_subcommands = {
  'ec2_tags'     : ec2_tags,
  'private_zone' : private_zone,
  'security_groups' : security_groups,
  'instance_roles' : instance_roles,
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


