import argparse

from pkg_resources import iter_entry_points

from botoform.enriched import EnrichedVPC

def get_profile_names():
    """Return a list of profile names in ~/.aws/config"""
    import botocore.session
    return botocore.session.get_session().full_config.get('profiles', {}).keys()

def load_entry_points(group_name):
    """Return a dictionary of entry_points related to given group_name"""
    entry_points = {}
    for entry_point in iter_entry_points(group=group_name, name=None):
        entry_points[entry_point.name] = entry_point.load()
    return entry_points

def load_parsers_from_plugins(subparser, plugins):
    """iterate over all plugins and load their parser."""
    for plugin_name, plugin_class in plugins.items():
        # create a parser object for the plugin.
        plugin_parser = subparser.add_parser(
                                    plugin_name,
                                    description = plugin_class.__doc__,
                                  )

        plugin_parser.add_argument('vpc_name', help='The VPC\'s Name tag.')

        try:
            # Assume class plugin with 'setup_parser' and 'main' staticmethods.
            plugin_class.setup_parser(plugin_parser)
            plugin_parser.set_defaults(func = plugin_class.main)
        except AttributeError:
            # Assume function plugin w/o 'setup_parser' or 'main' staticmethods.
            plugin_parser.set_defaults(func = plugin_class)

def build_parser(description, load_subparser_plugins=False):
    """build argparser and attach each plugin's parser to subparser."""
    parser = argparse.ArgumentParser(description = description)
    #requiredNamed = parser.add_argument_group('required named arguments')
    parser.add_argument('-p', '--profile', default='default',
      choices=get_profile_names(),
      help='botocore profile name for AWS creds and other vars.')
    parser.add_argument('-r', '--region', default=None,
      help='AWS region to use')
    #parser.add_argument('--search-regions', action='store_true', default=False,
    #  help='search regions for VPC with given vpc_name')
    #parser.add_argument('--quiet', action='store_true', default=False,
    #  help='prevent status messages to STDOUT')

    if load_subparser_plugins:
        # create a subparser for our plugins to attach to.
        subparser = parser.add_subparsers(
                          title = 'subcommands',
                          description = 'valid subcommands',
                          help = '--help for additional subcommand help'
                 )
        plugins = load_entry_points('botoform.plugins')
        load_parsers_from_plugins(subparser, plugins)
    else:
        parser.add_argument('vpc_name', help='The VPC\'s Name tag.')

    return parser

def get_evpc_from_args(args):
    if 'skip_evpc' not in args.__dict__:
        return EnrichedVPC(
                 vpc_name = args.vpc_name,
                 region_name = args.region,
                 profile_name = args.profile,
               )

def main():
    parser = build_parser('Manage infrastructure on AWS using YAML', True)
    args = parser.parse_args()
    evpc = get_evpc_from_args(args)
    # call the plugin main method.
    args.func(args, evpc)

if __name__ == '__main__':
    main()
