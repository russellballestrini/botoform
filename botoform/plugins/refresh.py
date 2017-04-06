from botoform.util import (
  output_formatter,
  key_value_to_dict,
  normalize_sg_rules,
)

from botoform.builders import EnvironmentBuilder

from botoform.config import ConfigLoader

from collections import defaultdict

no_cfg = {}

def get_builder_for_existing_vpc(evpc, args):
    # get extra_vars (context_vars) from command line.
    context_vars = key_value_to_dict(args.extra_vars)
    # get dictionary from ArgParse Namespace object and merge into context_vars.
    context_vars.update(vars(args))
    # add some vars from evpc object.
    context_vars.update({'vpc_name' : evpc.name, 'vpc_cidr' : evpc.cidr_block, 'region' : evpc.region_name})

    loader = ConfigLoader(context_vars = context_vars)
    config = loader.load(args.config)
    builder = EnvironmentBuilder(evpc.name, config, evpc.boto.region_name, evpc.boto.profile_name)
    builder.evpc = evpc
    builder.amis = config['amis']
    return builder

def tags(args, evpc):
    """
    Refresh tags.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args)
    builder.finish_instance_roles(builder.config.get('instance_roles', no_cfg))
    builder.tags(builder.config.get('tags', no_cfg))
    builder.log.emit('done tagging resources.')

def instance_roles(args, evpc):
    """
    Refresh ec2 instances and volumes, create missing ec2 resources.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args)
    instance_role_cfg = builder.config.get('instance_roles', no_cfg)
    builder.instance_roles(instance_role_cfg)
    builder.autoscaling_instance_roles(instance_role_cfg)
    builder.wait_for_instance_roles_to_exist(instance_role_cfg)
    builder.finish_instance_roles(instance_role_cfg)

def load_balancers(args, evpc):
    """
    Refresh elb Load_balancers.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args)
    builder.load_balancers(builder.config.get('load_balancers', no_cfg))

def private_zone(args, evpc):
    """
    Refresh private zone with new records / values.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args)
    builder.finish_instance_roles(builder.config.get('instance_roles', no_cfg))
    evpc.route53.create_private_zone()
    evpc.route53.refresh_private_zone()

def security_groups(args, evpc):
    """
    Refresh security_groups: add missing groups and rules.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    builder = get_builder_for_existing_vpc(evpc, args)

    security_groups_config = builder.config.get('security_groups', no_cfg)

    # build the missing security groups.
    builder.security_groups(security_groups_config)

    security_groups_current = evpc.enriched_security_groups
 
    rules_to_add = defaultdict(dict)
    rules_to_del = defaultdict(dict)

    for sg_name in security_groups_config:
        config  = security_groups_config[sg_name]
        current = security_groups_current[sg_name]

        config_inbound   = set(normalize_sg_rules(config.get('inbound', [])))
        current_inbound  = set(normalize_sg_rules(current.get('inbound', [])))

        config_outbound  = set(normalize_sg_rules(config.get('outbound', [])))
        current_outbound = set(normalize_sg_rules(current.get('outbound', [])))

        to_add_inbound  = list(config_inbound - current_inbound)
        to_add_outbound = list(config_outbound - current_outbound)

        #to_remove_inbound  = set(current.get('inbound', [])) - set(config.get('inbound',[]))
        #to_remove_outbound = set(current.get('outbound', [])) - set(config.get('outbound',[]))

        if len(to_add_inbound) != 0:
            rules_to_add[sg_name]['inbound'] = to_add_inbound

        if len(to_add_outbound) != 0:
            rules_to_add[sg_name]['outbound'] = to_add_outbound

    builder.security_group_rules(rules_to_add)


refresh_subcommands = {
  'tags'            : tags,
  'private_zone'    : private_zone,
  'instance_roles'  : instance_roles,
  'security_groups' : security_groups,
  'load_balancers'  : load_balancers,
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
        parser.add_argument('-e', '--extra-vars',
          default=list(), action='append', metavar='key=val',
          help='Extra Jinja2 context: --extra-vars key=val,key2=val2,key3=val3'
        )

    @staticmethod
    def main(args, evpc):
        refresh_subcommands[args.refresh_subcommand](args, evpc)


