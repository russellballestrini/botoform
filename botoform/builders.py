from botoform.enriched import EnrichedVPC

from botoform.util import (
  BotoConnections,
  add_tags,
)

import traceback

class EnvironmentBuilder(object):

    def __init__(self, config=None, region_name=None, profile_name=None):
        """
        config:
         The dict returned by botoform.config.ConfigLoader's load method.
        """
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

        vpc_name = config['vpc_name']
        cidrblock = config['cidrblock']

        self.build_vpc(vpc_name, cidrblock)

        # attach EnrichedVPC to self.
        self.evpc = EnrichedVPC(vpc_name, self.boto.region_name, self.boto.profile_name)

    def build_vpc(self, vpc_name, cidrblock):
        """Build VPC"""
        vpc = self.boto.ec2.create_vpc(CidrBlock = cidrblock)
        add_tags(vpc, Name = vpc_name)

        vpc.modify_attribute(EnableDnsSupport={'Value': True})
        vpc.modify_attribute(EnableDnsHostnames={'Value': True})

        # create internet_gateway.
        gw = self.boto.ec2.create_internet_gateway()
        add_tags(gw, Name = 'igw-' + vpc_name)

        # attach internet_gateway to VPC.
        vpc.attach_internet_gateway(
            DryRun=False,
            InternetGatewayId=gw.id,
            VpcId=vpc.id,
        )


