def destroy(args, evpc):
    """
    Destroy a VPC and related resources and services.
    
    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.

    :returns: None
    """ 
    evpc.terminate()

