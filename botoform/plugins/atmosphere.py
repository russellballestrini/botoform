from botoform.plugins import ClassPlugin

from botoform.util import (
  make_tag_dict,
  output_formatter,
)

from argparse import SUPPRESS

import botocore.session

import boto3

from nested_lookup import nested_lookup

def get_all_sessions():
    sessions = []
    aws_config = botocore.session.get_session().full_config
    for profile_name in aws_config['profiles']:
        session = botocore.session.Session(profile=profile_name)
        sessions.append(session)
    return sessions

def get_region_names(session):
    ec2 = session.create_client('ec2', region_name='us-east-1')
    return nested_lookup('RegionName', ec2.describe_regions())

class Atmosphere(ClassPlugin):
    """
    For every AWS profile + region, dump every VPC to STDOUT.

    This is a :ref:`class plugin` for the :ref:`bf` tool.
    """

    @staticmethod
    def setup_parser(parser):
        """
        Accepts a subparser and attaches additional arguments and flags.

        :param parser: An ArgumentParser sub parser.
            Reference: https://docs.python.org/3/library/argparse.html

        :returns: None
        """
        # remove the vpc_name positional argument, its not needed.
        vpc_name_positional_arg = parser._actions[-1]
        vpc_name_positional_arg.container._remove_action(vpc_name_positional_arg)

        parser.add_argument('--skip-evpc', default=True, help=SUPPRESS)
        parser.add_argument('--output-format',
          choices=['yaml', 'json'], default='yaml',
          help='the desired format of any possible output')

    @staticmethod
    def main(args, evpc=None):
        """
        For every AWS profile + region, dump every VPC to STDOUT.
        :param args: The parsed arguments and flags from the CLI.
        :returns: None
        """
        sessions = get_all_sessions()

        # We assume all sessions have the same list of regions.
        # This might not always be true. This is an optimization.
        regions = get_region_names(sessions[0])

        vpcs = {}

        for session in sessions:
            boto3.setup_default_session(profile_name=session.profile)
            vpcs[session.profile] = {}
            for region_name in regions:
                if region_name not in vpcs[session.profile]:
                    vpcs[session.profile][region_name] = {}
                ec2 = boto3.resource('ec2', region_name=region_name)
                for vpc in ec2.vpcs.all():
                    vpc_tags = make_tag_dict(vpc)
                    vpc_name = vpc_tags.get('Name', vpc.id)
                    vpcs[session.profile][region_name][vpc_name] = vpc.id

        print(output_formatter(vpcs, args.output_format))

