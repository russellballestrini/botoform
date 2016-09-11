from botoform.builders import EnvironmentBuilder

from botoform.config import ConfigLoader

from botoform.util import key_value_to_dict

from botoform.plugins import ClassPlugin

from argparse import SUPPRESS

class Create(ClassPlugin):
    """
    Create a new VPC and related services, modeled from YAML template.
    
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
        parser.add_argument('--skip-evpc', default=True, help=SUPPRESS)
        parser.add_argument('config',
          help='The botoform YAML config template.')
        parser.add_argument('-e', '--extra-vars',
          default=list(), action='append', metavar='key=val',
          help='Extra Jinja2 context: --extra-vars key=val,key2=val2,key3=val3'
        )
        parser.add_argument('-t', '--tags',
          default=list(), action='append', metavar='key=val',
          help='AWS resource: --tags key=val,key2=val2,key3=val3'
        )

    @staticmethod
    def main(args, evpc=None):
        """
        Creates a new VPC and related services, modeled from a YAML template.
       
        :param args: The parsed arguments and flags from the CLI.
        :param evpc: :meth:`botoform.enriched.vpc.EnrichedVPC` or None.

        :returns: None
        """
        # TODO: tags not implemented, not used. Pass to template or builder?
        aws_tags = key_value_to_dict(args.tags)

        # get extra_vars (context_vars) from command line.
        context_vars = key_value_to_dict(args.extra_vars)
        # get directionary from ArgParse Namespace object and merge into context_vars.
        context_vars.update(vars(args))

        loader = ConfigLoader(context_vars = context_vars)
        config = loader.load(template_path = args.config)
        ebuilder = EnvironmentBuilder(
                       args.vpc_name, config, args.region, args.profile)
        ebuilder.apply_all()


