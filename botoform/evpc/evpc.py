import boto3

from ..util import reflect_attrs

from instance import EnrichedInstance

class EnrichedVPC(object):
    """
    This class uses composition to enrich Boto3's VPC resource class.
    Here we relate AWS resources using various techniques like the vpc_name tag.
    We also provide methods for managing the lifecycle of related AWS resources.
    """

    def __init__(self, vpc_name=None, region_name=None, profile_name=None):
        """Create boto3 ec2 resource object and attach to self."""
        self.region_name = region_name
        if profile_name is not None:
            boto3.setup_default_session(profile_name = profile_name)

        # instantiate a boto3 ec2 resource object, attach to self.
        self.ec2 = boto3.resource('ec2', region_name = region_name)

        if vpc_name is not None:
            self.init(vpc_name)

    def init(self, vpc_name):
        """Finish init process, attach related Boto3 resources and clients."""
        self.vpc = self.get_vpc_by_name_tag(vpc_name)

        # reflect all attributes of boto3's vpc resource object into self.
        reflect_attrs(self, self.vpc)

        # attach a bunch of Boto3 resources and clients:
        self.rds = boto3.client('rds', region_name = self.region_name)
        self.elasticache = boto3.client('elasticache', region_name = self.region_name)

    def get_vpc_by_name_tag(self, vpc_name):
        """lookup vpc by vpc_name tag. Raises exceptions on insanity."""
        vpc_name_tag_filter = [{'Name':'tag:Name', 'Values':[vpc_name]}]
        vpcs = list(self.ec2.vpcs.filter(Filters=vpc_name_tag_filter))
        if len(vpcs) > 1:
            raise Exception('Multiple VPCs match tag Name:{}'.format(vpc_name))
        if len(vpcs) == 0:
            raise Exception('VPC not found with tag Name:{}'.format(vpc_name))
        return vpcs[0]

    def ec2_to_enriched_instances(self, ec2_instances):
        """Convert list of boto.ec2.instance.Instance to HuskyInstance"""
        return [EnrichedInstance(e, self) for e in ec2_instances]

    @property
    def einstances(self): 
        return self.ec2_to_enriched_instances(list(self.vpc.instances.all()))
