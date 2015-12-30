def lock(args, evpc):
    """Lock all instances in VPC to prevent termination."""
    evpc.lock_instances()

