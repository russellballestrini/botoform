from nested_lookup import nested_lookup

from ..util import (
  reflect_attrs,
  merge_pages,
)

class EnrichedElastiCache(object):

    def __init__(self, evpc):
        # save the HuskyVpc object.
        self.evpc = evpc
        # reflect all attributes of Client into EnrichedElastiCache.
        reflect_attrs(self, evpc.boto.elasticache)

    def get_all_subnet_group_descriptions(self):
        pages = self.get_paginator('describe_cache_subnet_groups').paginate()
        return merge_pages('CacheSubnetGroups', pages)

    def get_all_cluster_descriptions(self):
        pages = self.get_paginator(
                       'describe_cache_clusters'
                ).paginate(ShowCacheNodeInfo=True)
        return merge_pages('CacheClusters', pages)

    def get_related_subnet_group_descriptions(self):
        """return a list of cache subnet group descriptions related to VPC."""
        return filter(
                   lambda x : x['VpcId'] == self.evpc.vpc.id,
                   self.get_all_subnet_group_descriptions()
               )

    def get_related_cluster_descriptions(self):
        """return a list of cache cluster descriptions related to VPC."""
        subnet_descs = self.get_related_subnet_group_descriptions()
        subnet_names = nested_lookup('CacheSubnetGroupName', subnet_descs)
        return filter(
                   lambda x : x['CacheSubnetGroupName'] in subnet_names,
                   self.get_all_cluster_descriptions()
               )

    def get_related_cluster_endpoints(self):
        """return a list of cache cluster dns endpoints related to this VPC"""
        descriptions = self.get_related_cluster_descriptions()
        return nested_lookup('Endpoint', descriptions)

    def get_related_cluster_ids(self):
        """return a list of cache cluster ids related to this VPC"""
        descriptions = self.get_related_cluster_descriptions()
        return nested_lookup('CacheClusterId', descriptions)

    def wait_for_related_clusters(self, waiter_name, cluster_ids=None):
        """wait for related dbs to transition to desired state."""
        if cluster_ids is None:
            cluster_ids = self.get_related_cluster_ids()
        for cluster_id in cluster_ids:
            self.get_waiter(waiter_name).wait(CacheClusterId=cluster_id)

    def delete_related_cache_clusters(self, cluster_ids=None):
        """
        delete all cache clusters and subnet groups related to this VPC.
        cluster_ids:
            optional list of cache_cluster_ids (names) to delete instead.
        """
        cluster_descs = self.get_related_cluster_descriptions()
        related_cluster_ids = nested_lookup('CacheClusterId', cluster_descs)

        if cluster_ids is None:
            cluster_ids = related_cluster_ids
        else:
            # We make sure cluster_ids are part of this VPC.
            cluster_ids = [c for c in cluster_ids if c in related_cluster_ids]

        # get sibling cache cluster subnet group ids.
        subnet_ids = []
        for cluster_desc in cluster_descs:
            if cluster_desc['CacheClusterId'] in cluster_ids:
                subnet_ids.append(cluster_desc['CacheSubnetGroupName'])

        for cluster_id in cluster_ids:
            # delete the cache_cluster.
            self.delete_cache_cluster(CacheClusterId = cluster_id)

        # wait for all cluster_ids to reach cache_cluster_deleted state.
        self.wait_for_related_clusters('cache_cluster_deleted', cluster_ids)

        for subnet_id in subnet_ids:
            # delete the sibling cache_cluster_subnet_group.
            self.delete_cache_subnet_group(CacheSubnetGroupName = subnet_id)
            # delete the security_group for this cache_cluster.
            # we could get SecurityGroupId from describe...
            #self.evpc.get_security_group(cluster_id).delete()
