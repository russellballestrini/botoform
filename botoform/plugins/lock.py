def lock(args, evpc):
    """
    Lock all instances in VPC to prevent termination.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """ 
    evpc.lock_instances()

