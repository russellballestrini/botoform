import argparse

from pkg_resources import iter_entry_points

from botoform.enriched import EnrichedVPC

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

        try:
            # Assume class plugin with 'setup_parser' and 'main' staticmethods.
            plugin_class.setup_parser(plugin_parser)
            plugin_parser.set_defaults(func = plugin_class.main)
        except AttributeError:
            # Assume function plugin w/o 'setup_parser' or 'main' staticmethods.
            plugin_parser.set_defaults(func = plugin_class)

def build_parser(description):
    """build argparser and attach each plugin's parser to subparser."""
    parser = argparse.ArgumentParser(description = description)
    parser.add_argument('-p', '--profile', default=None,
      help='botocore profile name for AWS creds and other vars.')
    parser.add_argument('-r', '--region', default=None,
      help='AWS region to use')
    #parser.add_argument('--search-regions', action='store_true', default=False,
    #  help='search regions for VPC with given vpc_name')
    parser.add_argument('--quiet', action='store_true', default=False,
      help='prevent status messages to STDOUT')
    parser.add_argument('vpc_name')

    # create a subparser for our plugins to attach to.
    subparser = parser.add_subparsers(
                          title = 'subcommands',
                          description = 'valid subcommands',
                          help = '--help for additional subcommand help'
                 )

    plugins = load_entry_points('botoform.plugins')
    load_parsers_from_plugins(subparser, plugins)

    return parser

def main():
    parser = build_parser('Manage infrastructure on AWS using YAML')
    args = parser.parse_args()

    if 'skip_evpc' in args.__dict__:
        evpc = None
    else:
        evpc = EnrichedVPC(
                 vpc_name=args.vpc_name,
                 region_name=args.region,
                 profile_name=args.profile,
               )

    # call the plugin main ethod.
    args.func(args, evpc)

if __name__ == '__main__':
    main()
