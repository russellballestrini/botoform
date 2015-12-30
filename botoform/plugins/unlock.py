def unlock(args, evpc):
    """Lock all instances in VPC to prevent termination."""
    evpc.unlock_instances()

