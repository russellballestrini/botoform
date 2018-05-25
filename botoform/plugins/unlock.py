def unlock(args, evpc):
    """
    Unock all instances in VPC to allow termination.

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """
    evpc.unlock_instances()
