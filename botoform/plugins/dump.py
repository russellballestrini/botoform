import yaml
import json

class BotoformDumper(yaml.Dumper):
    """A custom YAML dumper that is pretty."""
    def increase_indent(self, flow=False, indentless=False):
        return super(BotoformDumper, self).increase_indent(flow, False)

def output(data, output_format='newline'):
    """Print data in the optional output_format."""
    if output_format.lower() == 'newline':
        output = '\n'.join(data)
    elif output_format.upper() == 'CSV':
        output = ', '.join(data)
    elif output_format.upper() == 'YAML':
        output = yaml.dump(data, Dumper=BotoformDumper)
    elif output_format.upper() == 'JSON':
        output = json.dumps(data, indent=2)
    print(output)

class Instances(object):
    """Output a list of instance names. (example botoform plugin)"""

    @staticmethod
    def setup_parser(parser):
        parser.add_argument('--all', action='store_true', default=False)
        parser.add_argument('--exclude', action='store_true', default=False)
        parser.add_argument('-r', '--roles',
          metavar='role', default=list(), nargs='*',
          help='examples: api ui persistence search proxy')
        parser.add_argument('-i', '--identifiers',
          metavar='identifier', default=list(), nargs='*',
          help='examples: custid-ui01 ui01 192.168.1.9 i-01234567')
        parser.add_argument('--output-format',
          choices=['csv', 'yaml', 'json', 'newline'], default='newline',
          help='the desired format of any possible output')

    @staticmethod
    def main(args, evpc):
        """Output a list of instance names. (example botoform plugin)"""
        if args.all:
            instances = evpc.instances
        else:
            instances = evpc.find_instances(args.identifiers, args.roles, args.exclude)
        output(map(str, instances), args.output_format)


class SecurityGroups(object):
    """Output a list of security groups and rules. (example botoform plugin)"""

    @staticmethod
    def setup_parser(parser):
        parser.add_argument('--output-format',
          choices=['csv', 'yaml', 'json', 'newline'], default='yaml',
          help='the desired format of any possible output')

    @staticmethod
    def main(args, evpc):
        """Output Security Groups in a Botoform compatible format."""
        sgs = list(evpc.security_groups.all())
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
                        related_sg = evpc.ec2.SecurityGroup(id=pair['GroupId'])
                        rule.append(related_sg.group_name)
                        rule.append(ip_protocol)
                        rule.append(port_range)
                        sgs[sg.group_name].append(rule)

        output({'security_groups' : sgs}, args.output_format)


