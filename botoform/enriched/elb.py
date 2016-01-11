from ..util import (
  reflect_attrs,
  merge_pages,
)

from nested_lookup import nested_lookup

class EnrichedElb(object):

    def __init__(self, evpc):
        # save the EnrichedVpc object.
        self.evpc = evpc

        # capture a list of this classes attributes before reflecting.
        self.self_attrs = dir(self)

        # reflect all connection attributes into EnrichedElb.
        reflect_attrs(self, self.evpc.boto.elb, self.self_attrs)

    def get_all_elb_descriptions(self):
        """Return a list of all ELB (Load Balancer) descriptions."""
        pages = self.get_paginator('describe_load_balancers').paginate()
        return merge_pages('LoadBalancerDescriptions', pages)

    def get_related_elb_descriptions(self):
        """Return a list of related ELB (Load Balancer) descriptions."""
        descriptions = []
        for elb in self.get_all_elb_descriptions():
            if elb['VPCId'] == self.evpc.vpc.id:
                descriptions.append(elb)
        return descriptions

    def get_related_elb_names(self):
        """Return a list of related ELB (Load Balancer) names."""
        return nested_lookup(
                   'LoadBalancerName',
                   self.get_related_elb_descriptions(),
               )

    # TODO:
    # 1. method to refresh related elb registrations & wait until in service.
    # 2. method to create a new related elb.
    # 3. method to delete related elbs.
