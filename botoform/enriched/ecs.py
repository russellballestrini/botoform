from nested_lookup import nested_lookup

from ..util import reflect_attrs, merge_pages


class EnrichedEcs(object):

    def __init__(self, evpc):
        # save the EnrichedVpc object.
        self.evpc = evpc

        # capture a list of this classes attributes before reflecting.
        self.self_attrs = dir(self)

        # reflect all attributes of Client into EnrichedEcs.
        reflect_attrs(self, self.evpc.boto.ecs_client, self.self_attrs)

    def list_all_service_arns(self, cluster):
        """
        :param cluster: The short name or full Amazon Resource Name (ARN)
                        of the cluster that hosts the services to list.
        """
        pages = self.get_paginator("list_services").paginate(cluster=cluster)
        return merge_pages("serviceArns", pages)
