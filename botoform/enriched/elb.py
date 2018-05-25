from ..util import reflect_attrs, merge_pages, get_ids

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
        pages = self.get_paginator("describe_load_balancers").paginate()
        return merge_pages("LoadBalancerDescriptions", pages)

    def get_related_elb_descriptions(self):
        """Return a list of related ELB (Load Balancer) descriptions."""
        descriptions = []
        for elb in self.get_all_elb_descriptions():
            if elb["VPCId"] == self.evpc.vpc.id:
                descriptions.append(elb)
        return descriptions

    def get_related_elb_names(self):
        """Return a list of related ELB (Load Balancer) names."""
        return nested_lookup("LoadBalancerName", self.get_related_elb_descriptions())

    def format_listeners(self, listener_tuples):
        listener_dicts = []
        for listener in listener_tuples:
            listener_dicts.append(
                {
                    "LoadBalancerPort": listener[0],
                    "InstancePort": listener[1],
                    "Protocol": listener[2],
                    "InstanceProtocol": listener[2],
                }
            )
        return listener_dicts

    def format_instance_ids(self, instance_ids):
        """god boto3 is a pain sometimes."""
        return [{"InstanceId": instance_id} for instance_id in instance_ids]

    def register_role_with_load_balancer(self, elb_name, role_name):
        role = self.evpc.get_role(role_name)
        instance_ids = get_ids(role)
        self.register_instances_with_load_balancer(
            LoadBalancerName=elb_name, Instances=self.format_instance_ids(instance_ids)
        )

    def delete_related_elbs(self):
        for elb_name in self.get_related_elb_names():
            self.evpc.log.emit("deleting load balancer: {}".format(elb_name))
            self.delete_load_balancer(LoadBalancerName=elb_name)
