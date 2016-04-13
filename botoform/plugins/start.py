def start(args, evpc):
    """
    Start all the instances in VPC.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    evpc.start_instances()
