from argparse import SUPPRESS

class ClassPlugin(object):
    """This is a :ref:`class plugin` for the :ref:`bf` tool."""

    @staticmethod
    def setup_parser(parser):
        """
        Accepts a subparser and attaches additional arguments and flags.

        :param parser: An ArgumentParser sub parser.
            Reference: https://docs.python.org/3/library/argparse.html

        :returns: None
        """
        pass

    @staticmethod
    def main(args, evpc=None):
        """
        The main logic for this plugin.
       
        :params args: The parsed arguments and flags from the CLI.
        :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

        :returns: None
        """
        pass

    @staticmethod
    def remove_vpc_name_from_parser(parser):
        """
        Accepts a subparser and removes the vpc_name positional argument.

        Use if your tool does not need the vpc_name positional argument.

        For example, in your custom `setup_parser`::

          ClassPlugin.remove_vpc_name_from_parser(parser)

        :param parser: An ArgumentParser sub parser.
            Reference: https://docs.python.org/3/library/argparse.html

        :returns: None
        """
        vpc_name_positional_arg = parser._actions[-1]
        vpc_name_positional_arg.container._remove_action(vpc_name_positional_arg)
        parser.add_argument('--skip-evpc', default=True, help=SUPPRESS)
