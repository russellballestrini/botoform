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


