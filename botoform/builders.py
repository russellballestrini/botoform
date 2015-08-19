from botoform.enriched import EnrichedVPC

from botoform.util import (
  BotoConnections,
  update_tags,
)

import traceback

class EnvironmentBuilder(object):

    def __init__(self, vpc_name, config=None, region_name=None, profile_name=None):
        """
        vpc_name:
         The human readable Name tag of this VPC.

        config:
         The dict returned by botoform.config.ConfigLoader's load method.
        """
        self.vpc_name = vpc_name
        self.config = config if config is not None else {}
        self.boto = BotoConnections(region_name, profile_name)

    def build(self):
        """
        Build the environment specified in the config.
        """
        try:
            self._build(self.config)
        except Exception as e:
            print("Failed to build Botoform Environment! Tearing down!")
            print("Failure reason: %s" % (e))
            print("Stack Trace\n-----\n%s\n-----" % (traceback.format_exc()))
            #self.evpc.terminate()
            raise

    def _build(self, config):

        # set a var for no_cfg.
        no_cfg = {}

        self.build_vpc(config['cidrblock'])

        # attach EnrichedVPC to self.
        self.evpc = EnrichedVPC(self.vpc_name, self.boto.region_name, self.boto.profile_name)

    def build_vpc(self, cidrblock):
        """Build VPC"""
        vpc = self.boto.ec2.create_vpc(CidrBlock = cidrblock)
        update_tags(vpc, Name = self.vpc_name)

        vpc.modify_attribute(EnableDnsSupport={'Value': True})
        vpc.modify_attribute(EnableDnsHostnames={'Value': True})

        # create internet_gateway.
        gw = self.boto.ec2.create_internet_gateway()
        update_tags(gw, Name = 'igw-' + self.vpc_name)

        # attach internet_gateway to VPC.
        vpc.attach_internet_gateway(
            DryRun=False,
            InternetGatewayId=gw.id,
            VpcId=vpc.id,
        )


