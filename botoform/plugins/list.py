from botoform.plugins import ClassPlugin

from botoform.util import BotoConnections, make_tag_dict, output_formatter


class ListVpcs(ClassPlugin):
    """
    List all VPC names to STDOUT for a given AWS profile + region.

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
        ClassPlugin.remove_vpc_name_from_parser(parser)
        parser.add_argument(
            "--output-format",
            choices=["yaml", "json"],
            default="yaml",
            help="the desired format of any possible output",
        )

    @staticmethod
    def main(args, evpc=None):
        """
        List all VPC names to STDOUT for a given AWS profile + region.

        :param args: The parsed arguments and flags from the CLI.
        :returns: None
        """
        vpc_names = []
        bconn = BotoConnections(args.region, args.profile)
        for vpc in bconn.ec2.vpcs.all():
            vpc_tags = make_tag_dict(vpc)
            vpc_name = vpc_tags.get("Name", vpc.id)
            vpc_names.append(vpc_name)
        print(output_formatter(vpc_names, args.output_format))
