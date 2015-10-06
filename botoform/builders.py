from botoform.enriched import EnrichedVPC

from botoform.util import (
  BotoConnections,
  Log,
  update_tags,
)

import traceback

class EnvironmentBuilder(object):

    def __init__(self, vpc_name, config=None, region_name=None, profile_name=None, log=None):
        """
        vpc_name:
         The human readable Name tag of this VPC.

        config:
         The dict returned by botoform.config.ConfigLoader's load method.
        """
        self.vpc_name = vpc_name
        self.config = config if config is not None else {}
        self.log = log if log is not None else Log()
        self.boto = BotoConnections(region_name, profile_name)

    def build(self):
        """
        Build the environment specified in the config.
        """
        try:
            self._build(self.config)
        except Exception as e:
            self.log.emit('Botoform failed to build environment!', 'error')
            self.log.emit('Failure reason: {}'.format(e), 'error')
            self.log.emit(traceback.format_exc(), 'debug')
            self.log.emit('Tearing down failed environment!', 'error')
            #self.evpc.terminate()
            raise

    def _build(self, config):

        # set a var for no_cfg.
        no_cfg = {}

        self.build_vpc(config['cidrblock'])

        # attach EnrichedVPC to self.
        self.evpc = EnrichedVPC(self.vpc_name, self.boto.region_name, self.boto.profile_name)

        try:
            self.evpc.lock_instances()
        except:
            self.log.emit('Could not lock instances, continuing...', 'warning')

    def build_vpc(self, cidrblock):
        """Build VPC"""
        self.log.emit('creating vpc ({}, {})'.format(self.vpc_name, cidrblock))
        vpc = self.boto.ec2.create_vpc(CidrBlock = cidrblock)

        self.log.emit('tagging vpc (Name:{})'.format(self.vpc_name), 'debug')
        update_tags(vpc, Name = self.vpc_name)

        self.log.emit('modifying vpc for dns support', 'debug')
        vpc.modify_attribute(EnableDnsSupport={'Value': True})
        self.log.emit('modifying vpc for dns hostnames', 'debug')
        vpc.modify_attribute(EnableDnsHostnames={'Value': True})

        igw_name = 'igw-' + self.vpc_name
        self.log.emit('creating internet_gateway ({})'.format(igw_name))
        gw = self.boto.ec2.create_internet_gateway()
        self.log.emit('tagging gateway (Name:{})'.format(igw_name), 'debug')
        update_tags(gw, Name = igw_name)

        self.log.emit('attaching igw to vpc ({})'.format(igw_name))
        vpc.attach_internet_gateway(
            DryRun=False,
            InternetGatewayId=gw.id,
            VpcId=vpc.id,
        )


