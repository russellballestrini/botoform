import netaddr

def allocate(cidrs, sizes):
    """
    Accept network block CIDRs and list of subnetwork CIDR sizes.
    Return a list of IPNetwork objects allocated from the network block.
    
    For example::
    
      >>> allocate('10.10.10.0/24', [27,27,28,29])
      [IPNetwork('10.10.10.0/27'), IPNetwork('10.10.10.32/27'), IPNetwork('10.10.10.64/28'), IPNetwork('10.10.10.80/29')]
    """

    if isinstance(cidrs, str):
        cidrs = [netaddr.IPNetwork(cidrs)]

    if len(sizes) == 0:
        return []

    sizes = sorted(sizes)
    need_size = sizes[0]
    need_count = sizes.count(need_size)
    sizes = sizes[need_count:]

    allocated_cidrs = []
    remaining_cidrs = []

    for c in cidrs:
        if need_count == 0:
            remaining_cidrs.append(c)
            continue

        subnets = list(c.subnet(need_size))

        if need_count > len(subnets):
            allocated_cidrs += subnets
            need_count -= len(subnets)
        else:
            allocated_cidrs += subnets[0:need_count]
            remaining_cidrs += subnets[need_count:]
            need_count = 0

    if need_count != 0:
        raise Exception("Not enough room! Need %d more subnets of size %d but can't get any" % (need_count, need_size))

    # Split off remainder and allocate that
    allocated_cidrs += allocate(remaining_cidrs, sizes)
    return allocated_cidrs
