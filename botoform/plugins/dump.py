from botoform.util import output_formatter

def ansible_hosts(args, evpc):
    """
    Output an Ansible host inventory for the VPC.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: Ansible inventory to standard out.
    """
    instance_line = "{} eip={} name={} id={}"
    roles = evpc.roles
    print('[' + evpc.name + ':children]')
    for role in roles:
        print(role)
    print('')
    for role, instances in roles.items():
        print('[' + role + ']')
        for i in instances:
            print(
              instance_line.format(
                i.private_ip_address,
                i.public_ip_address,
                i.name,
                i.id,
                i.id_human,
              )
            )
        print('')

def instances(args, evpc):
    """
    Output instance roles to standard out in :ref:`Botoform Schema <schema reference>`.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: instance_roles to standard out in :ref:`Botoform Schema <schema reference>`.
    """
    if args.identifiers or args.roles or args.exclude:
        instances = evpc.find_instances(args.identifiers, args.roles, args.exclude)
    else:
        instances = evpc.instances
    print(output_formatter(map(lambda i : i.identifiers, instances), args.output_format))

def security_groups(args, evpc):
    """
    Output Security Groups to standard out in :ref:`Botoform Schema <schema reference>`.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: security_groups to standard out in :ref:`Botoform Schema <schema reference>`.
    """ 
    sgs = {'security_groups' : evpc.enriched_security_groups}
    print(output_formatter(sgs, args.output_format))

dump_subcommands = {
  'instances'       : instances,
  'security_groups' : security_groups,
  'ansible_hosts'   : ansible_hosts,
}

class Dump(object):
    """
    Dump AWS resourses as :ref:`Botoform Schema <schema reference>`.
    
    This is a :ref:`class plugin` for the :ref:`bf` tool.
    """

    @staticmethod
    def setup_parser(parser):
        # TODO: break each subcommand into subparsers with different args.
        parser.add_argument('dump_subcommand', choices=dump_subcommands)
        parser.add_argument('--output-format',
          choices=['csv', 'yaml', 'json', 'newline'], default='yaml',
          help='the desired format of any possible output')
        parser.add_argument('--exclude', action='store_true', default=False,
          help='make qualifiers exclude instead of include!')
        parser.add_argument('-r', '--roles',
          metavar='role', default=list(), nargs='*',
          help='examples: api ui persistence search proxy')
        parser.add_argument('-i', '--identifiers',
          metavar='identifier', default=list(), nargs='*',
          help='examples: custid-ui01 ui01 192.168.1.9 i-01234567')

    @staticmethod
    def main(args, evpc):
        dump_subcommands[args.dump_subcommand](args, evpc)


