from ..util import (
  reflect_attrs,
  merge_pages,
  get_ids,
)

from nested_lookup import nested_lookup

class EnrichedAutoscaling(object):

    def __init__(self, evpc):
        # save the EnrichedVpc object.
        self.evpc = evpc

        # capture a list of this classes attributes before reflecting.
        self.self_attrs = dir(self)

        # reflect all connection attributes into EnrichedElb.
        reflect_attrs(self, self.evpc.boto.autoscaling, self.self_attrs)

    def get_all_autoscaling_group_descriptions(self):
        """Return a list of all autoscaling groups descriptions."""
        pages = self.get_paginator('describe_auto_scaling_groups').paginate()
        return merge_pages('AutoScalingGroups', pages)

    def get_related_autoscaling_group_descriptions(self):
        """Return a list of related autoscaling groups descriptions."""
        descriptions = []
        # get this vpc's subnet_ids.
        vpc_subnet_ids = get_ids(self.evpc.subnets.all())
        for asg in self.get_all_autoscaling_group_descriptions():
            # autoscaling descriptions hold subnets as CSV string, so we create a set.
            asg_subnet_ids = set(asg['VPCZoneIdentifier'].split(','))
            # we compare the subnet_ids from asg and vpc and assume relations on intersections.
            if asg_subnet_ids.intersection(vpc_subnet_ids):
                descriptions.append(asg)
        return descriptions

    def get_all_launch_config_descriptions(self):
        """Return a list of all launch configuration descriptions."""
        pages = self.get_paginator('describe_launch_configurations').paginate()
        return merge_pages('LaunchConfigurations', pages)

    def get_related_launch_config_descriptions(self):
        """Return a list of related launch configuration descriptions."""
        descriptions = []
        # get this vpc's security_group_ids.
        vpc_security_group_ids = get_ids(self.evpc.security_groups.all())
        for lc in self.get_all_launch_config_descriptions():
            lc_security_group_ids = set(lc['SecurityGroups'])
            # we compare the security_group ids from lc and vpc and assume relations on intersections.
            if lc_security_group_ids.intersection(vpc_security_group_ids):
                descriptions.append(lc)
        return descriptions
