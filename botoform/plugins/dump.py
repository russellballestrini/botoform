from botoform.util import output_formatter

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
    print(output_formatter(map(str, instances), args.output_format))

def security_groups(args, evpc):
    """
    Output Security Groups to standard out in :ref:`Botoform Schema <schema reference>`.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: security_groups to standard out in :ref:`Botoform Schema <schema reference>`.
    """ 
    sgs = {}
    for sg in evpc.security_groups.all():
        sgs[sg.group_name] = []
        for perm in sg.ip_permissions:
            ip_protocol = perm['IpProtocol']
            from_port = perm.get('FromPort', -1)
            to_port   = perm.get('ToPort', -1)
            port_range = from_port
            if from_port != to_port:
                port_range = '{}-{}'.format(from_port, to_port)
            if len(perm['IpRanges']) >= 1:
                for iprange in perm['IpRanges']:
                    rule = []
                    rule.append(iprange['CidrIp'])
                    rule.append(ip_protocol)
                    rule.append(port_range)
                    sgs[sg.group_name].append(rule)
            if len(perm['UserIdGroupPairs']) >= 1:
                for pair in perm['UserIdGroupPairs']:
                    rule = []
                    related_sg = evpc.boto.ec2.SecurityGroup(id=pair['GroupId'])
                    rule.append(related_sg.group_name)
                    rule.append(ip_protocol)
                    rule.append(port_range)
                    sgs[sg.group_name].append(rule)

    print(output_formatter({'security_groups' : sgs}, args.output_format))

dump_subcommands = {
  'instances'       : instances,
  'security_groups' : security_groups,
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


