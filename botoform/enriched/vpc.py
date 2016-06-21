import time

from botoform.util import (
  BotoConnections,
  Log,
  reflect_attrs,
  make_tag_dict,
  make_filter,
  tag_filter,
  update_tags,
  write_private_key,
)

from instance import EnrichedInstance
from vpc_endpoint import EnrichedVpcEndpoint
from autoscaling import EnrichedAutoscaling
from elasticache import EnrichedElastiCache
from elb import EnrichedElb
from rds import EnrichedRds
from key_pair import EnrichedKeyPair

from nested_lookup import nested_lookup

class EnrichedVPC(object):
    """
    This class uses composition to enrich Boto3's VPC resource class.
    Here we relate AWS resources using various techniques like the vpc_name tag.
    We also provide methods for managing the lifecycle of related AWS resources.
    """

    def __init__(self, vpc_name=None, region_name=None, profile_name=None, log=None):
        self.boto = BotoConnections(region_name, profile_name)

        # capture a list of this classes attributes before reflecting.
        self.self_attrs = dir(self)

        self.log = log if log is not None else Log()
        
        if vpc_name is not None:
            self.vpc_name = vpc_name
            self.connect(vpc_name)

    def __str__(self):
        return self.identity

    def _get_vpcs_by_filter(self, vpc_filter):
        # external API call to AWS.
        return list(self.boto.ec2.vpcs.filter(Filters=vpc_filter))

    def get_vpc_by_name_tag(self, vpc_name):
        """lookup vpc by vpc_name tag. Raises exceptions on insanity."""
        vpcs = self._get_vpcs_by_filter(tag_filter('Name', vpc_name))
        if len(vpcs) > 1:
            raise Exception('Multiple VPCs match tag Name:{}'.format(vpc_name))
        if len(vpcs) == 0:
            raise Exception('VPC not found with tag Name:{}'.format(vpc_name))
        return vpcs[0]

    def reflect_attrs(self):
        """reflect all attributes of boto3's vpc resource object into self."""
        reflect_attrs(self, self.vpc, skip_attrs=self.self_attrs)

    def reload(self):
        """run the reload method on the attached instance and reflect_attrs."""
        self.vpc.reload()
        self.reflect_attrs()

    def connect(self, vpc_name):
        """connect to VPC and reflect all attributes into self."""
        self.vpc = self.get_vpc_by_name_tag(vpc_name)

        self.reflect_attrs()

        # attach Enriched Connections to self.
        self.vpc_endpoint = EnrichedVpcEndpoint(self)
        self.autoscaling = EnrichedAutoscaling(self)
        self.elasticache = EnrichedElastiCache(self)
        self.elb = EnrichedElb(self)
        self.rds = EnrichedRds(self)
        self.key_pair = EnrichedKeyPair(self)

    @property
    def region_name(self): return self.boto.region_name

    @property
    def azones(self): return self.boto.azones

    @property
    def tag_dict(self):
        return make_tag_dict(self.vpc)

    @property
    def name(self): return self.tag_dict.get('Name', None)

    @property
    def identity(self): return self.name or self.id

    def _ec2_instances(self):
        # external API call to AWS.
        return self.vpc.instances.all()

    def _ec2_to_enriched_instances(self, ec2_instances):
        """Convert list of boto.ec2.instance.Instance to EnrichedInstance"""
        return [EnrichedInstance(e, self) for e in ec2_instances]

    def get_instances(self, instances=None):
        """
        Returns a possibly empty list of EnrichedInstance objects.

        :param instances:
          Optional, list or collection to convert to EnrichedInstance objects.

        :returns: list of EnrichedInstance objects
        """
        instances = self._ec2_instances() if instances is None else instances
        return self._ec2_to_enriched_instances(instances)

    def get_running_instances(self, instances=None):
        """Return list running EnrichedInstance object related to this VPC."""
        return [i for i in self.get_instances(instances) if i.state['Code'] == 16]

    def get_roles(self, instances=None):
        """
        Return a dict of lists where role is the key and
        a list of EnrichedInstance objects is the value.
        """
        roles = {}
        for instance in self.get_instances(instances):
            if instance.role not in roles:
                roles[instance.role] = []
            roles[instance.role].append(instance)
        return roles

    def get_role(self, role_name, instances=None):
        """
        Return a possibly empty list of EnrichedInstance objects.

        :param role_name:
          The name of the role whose instances to return.
        :param instances:
          Optional, list or collection to search role from.

        :returns: A list of EnrichedInstance objects.
        """
        return self.get_roles(instances).get(role_name, [])

    def find_instance(self, identifier):
        """
        Return an instance or None which matches identifier.

        Raises exception if multiple instances match identifier.

        :param identifier:
          A list of identifiers to qualify instances by, for example:
            * custid-ui01
            * ui01
            * 192.168.1.9
            * i-01234567

        :returns: EnrichedInstance or None
        """
        instances = []
        for instance in self.get_instances():
            if identifier in instance.identifiers:
                instances.append(instance)
        if len(instances) > 1:
            msg = "Multiple instances '{}' have '{}' identifier."
            instance_names = ', '.join(map(str, instances))
            raise Exception(msg.format(instance_names, identifier))
        if len(instances) == 0:
            return None
        return instances[0]

    @staticmethod
    def _set(x):
        """Return a set of the given iterable, return emtpy set if None."""
        return set() if x is None else set(x)

    def _identify_instance(self, i, identifiers, roles):
        """Return True if instance is identified / qualified, else False"""
        identifiers = self._set(identifiers)
        roles       = self._set(roles)
        return bool(identifiers.intersection(i.identifiers) or i.role in roles)

    def find_instances(self, identifiers=None, roles=None, exclude=False):
        """
        Accept a list of identifiers and/or roles.
        Return a list of instances which match either qualifier list.

        :param identifiers:
          Optional, a list of identifiers to qualify instances by, for example:
            * custid-ui01
            * ui01
            * 192.168.1.9
            * i-01234567

        :param roles:
          Optional, a list of roles to qualify instances by, for example:
            * ui
            * api
            * proxy

        :param exclude:
          If True, qualifiers exclude instead of include!
          Defaults to False.

        Danger:
          This method will return *no* instances if all qualifiers are None.
          However, if *exclude* is True we could return *all* instances!

        :returns: A list of EnrichedInstance objets or an empty list.
        """
        instances = []
        for i in self.get_instances():
            qualified = self._identify_instance(i, identifiers, roles)
            if qualified and exclude == False:
                instances.append(i)
            elif not qualified and exclude == True:
                instances.append(i)
        return instances

    def include_instances(self, identifiers = None, roles = None):
        """
        Accept a list of identifiers and/or roles.
        Return a list of instances which match either qualifier list.

        Note:
         This method returns no instances if both identfiers and roles is None.
        """
        return self.find_instances(identifiers, roles, exclude=False)

    def exclude_instances(self, identifiers = None, roles = None):
        """
        Accept a list of identifiers and/or roles.
        Return a list of instances which do *not* match either qualifier list.

        Note:
         This method returns all instances if both identfiers and roles is None.
        """
        return self.find_instances(identifiers, roles, exclude=True)

    @property
    def instances(self): return self.get_instances()

    @property
    def roles(self): return self.get_roles()

    def get_main_route_table(self):
        """Return the main (default) route table for VPC."""
        main_route_table = []
        for route_table in self.route_tables.all():
            for association in route_table.associations.all():
                if association.main == True:
                    main_route_table.append(route_table)
        if len(main_route_table) != 1:
            raise Exception('cannot get main route table! {}'.format(main_route_table))
        return main_route_table[0]

    def _filter_collection_by_name(self, name, collection):
        names = [name, '{}-{}'.format(self.name, name)]
        objs = list(collection.filter(Filters=tag_filter('Name', names)))
        return objs[0] if len(objs) == 1 else None

    def get_route_table(self, name):
        """Accept route table name, return route_table object or None."""
        return self._filter_collection_by_name(name, self.route_tables)

    def get_subnet(self, name):
        """Accept subnet name, return subnet object or None."""
        return self._filter_collection_by_name(name, self.subnets)

    def get_security_group(self, name):
        """Accept security group name, return security group object or None."""
        return self._filter_collection_by_name(name, self.security_groups)

    def get_vpn_gateways(self):
        """Gets all the VGWs attached to the VPC"""
        vgws = self.boto.ec2_client.describe_vpn_gateways(
            Filters=[
                     {
                       'Name': 'attachment.vpc-id',
                       'Values': [ self.id, ] 
                     }, 
                    ]
        )
        return vgws.get('VpnGateways', {})
    
    def associate_route_table_with_subnet(self, rt_name, sn_name):
        """Accept a route table name and subnet name, associate them."""
        self.boto.ec2_client.associate_route_table(
                        RouteTableId = self.get_route_table(rt_name).id,
                        SubnetId     = self.get_subnet(sn_name).id,
        )

    def lock_instances(self, instances=None):
        """Lock all or a list of instances."""
        for instance in self.get_instances(instances):
            instance.lock()

    def unlock_instances(self, instances=None):
        """Unlock all or a list of instances."""
        for instance in self.get_instances(instances):
            instance.unlock()

    def is_vgw_attached(self, vgw_id):
        """Check whether the VGW is attached or not"""
        vgw = self.boto.ec2_client.describe_vpn_gateways(
                    VpnGatewayIds=[vgw_id]
                )
        return vgw.get('VpnGateways')[0].get('VpcAttachments')[0].get('State') == 'attached'

    def is_vgw_detached(self, vgw_id):
        """Check whether the VGW is attached or not"""
        vgw = self.boto.ec2_client.describe_vpn_gateways(
                    VpnGatewayIds=[vgw_id]
                )
        return vgw.get('VpnGateways')[0].get('VpcAttachments')[0].get('State') == 'detached'
        
    def attach_vpn_gateway(self, vgw_id):
        """Attach VPN gateway to the VPC"""
        self.vgw_id = vgw_id
        self.boto.ec2_client.attach_vpn_gateway(
                    DryRun=False,
                    VpnGatewayId = self.vgw_id,
                    VpcId = self.id,                                    
                )
        # check & wait till VGW (2 min.) is attached
        count = 0
        while(not self.is_vgw_attached(vgw_id)):
            self.log.emit('\tattaching...', 'debug')
            time.sleep(10)
            count += 1
            if count == 11:
                raise Exception({"message":"VPN Gateway is not yet attached.", "VGW_ID":vgw_id})
     
    def detach_vpn_gateway(self):
        """Detach VPN gateway from VPC"""
        for vgw in self.get_vpn_gateways():
            vgw_id = vgw.get('VpnGatewayId')
            self.log.emit('detaching vgw - {} from vpc - {}'.format(vgw_id, self.vpc_name))
            self.boto.ec2_client.detach_vpn_gateway(
                        DryRun=False,
                        VpnGatewayId = vgw_id,
                        VpcId = self.id,                                    
                    )
            # check & wait till VGW (2 min.) is detached
            self.log.emit('\tdetaching...', 'debug')
            time.sleep(10)
            count = 0
            while(not self.is_vgw_detached(vgw_id)):
                self.log.emit('\tdetaching...', 'debug')
                time.sleep(10)
                count += 1
                if count == 11:
                    raise Exception({"message":"VPN Gateway is not yet detached.", "VGW_ID":vgw_id})

    def create_dhcp_options(self, data):
        """Creates DHCP Options Set"""
        dhcp_configurations = []
        for k, v in data.items():
            self.log.emit('\tDHCP Options - {} = {}'.format(k, v))
            dhcp_configurations.append(
                {
                    'Key': k,
                    'Values': v
                }
            )
        
        dhcp_options = self.boto.ec2_client.create_dhcp_options(
                            DhcpConfigurations=dhcp_configurations
                        )
        dhcp_options_id = dhcp_options.get('DhcpOptions').get('DhcpOptionsId')
        self.dhcp_options = self.boto.ec2.DhcpOptions(dhcp_options_id)
        return dhcp_options_id
        
    def wait_until_instances(self, instances=None, state=None):
        instances = self.get_instances(instances)
        msg = 'waiting for {} to transition to {}'
        for instance in instances:
            self.log.emit(msg.format(instance.identity, state))
            if state == 'running':
                instance.wait_until_running()
            if state == 'stopped':
                instance.wait_until_stopped()
            if state == 'terminated':
                instance.wait_until_terminated()

    def stop_instances(self, instances=None, wait=True):
        """Stop all or a list of instances."""
        instances = self.get_instances(instances)
        for instance in instances:
            self.log.emit('stopping {} instance ...'.format(instance.identity))
            instance.stop()
        if wait == True:
            self.wait_until_instances(instances, 'stopped')

    def start_instances(self, instances=None, wait=True):
        """Start all or a list of instances."""
        instances = self.get_instances(instances)
        for instance in instances:
            self.log.emit('starting {} instance ...'.format(instance.identity))
            instance.start()
        if wait == True:
            self.wait_until_instances(instances, 'running')
        
    def delete_instances(self, instances=None, wait=True):
        """Terminate all or a list of instances."""
        instances = self.get_instances(instances)
        for instance in instances:
            self.log.emit('terminating {} instance ...'.format(instance.identity))
            instance.disassociate_eips()
            instance.terminate()
        if wait == True:
            self.wait_until_instances(instances, 'terminated')

    def delete_internet_gateways(self):
        """Delete related internet gatways."""
        for igw in self.internet_gateways.all():
            self.log.emit('detaching internet gateway - {} from vpc - {}'.format(igw.id, self.vpc_name))
            igw.detach_from_vpc(VpcId = self.id)
            self.log.emit('deleting internet gateway - {}'.format(igw.id))
            igw.delete()

    def delete_security_groups(self):
        """Delete related security groups."""
        for sg in self.security_groups.all():
            if len(sg.ip_permissions) >= 1:
                self.log.emit('revoking all inbound rules of security group - {}'.format(sg.id))
                sg.revoke_ingress(IpPermissions = sg.ip_permissions)

            if len(sg.ip_permissions_egress) >= 1:
                self.log.emit('revoking all outbound rules of security group - {}'.format(sg.id))
                sg.revoke_egress(IpPermissions = sg.ip_permissions_egress)

        for sg in self.security_groups.all():
            if sg.group_name == 'default':
                continue
            self.log.emit('deleting security group - {}'.format(sg.id))
            sg.delete()

    def delete_subnets(self):
        """Delete related subnets."""
        for sn in self.subnets.all():
            self.log.emit('deleting subnet - {}'.format(sn.id))
            sn.delete()

    def delete_route_tables(self):
        """Delete related route tables."""
        main_rt = self.get_main_route_table()
        for rt in self.route_tables.all():
            if rt.id != main_rt.id:
                for a in rt.associations.all():
                    self.log.emit('dissociating subnet {} from route table {}'.format(a.subnet_id, a.route_table_id))
                    a.delete()
                self.log.emit('deleting route table {}'.format(rt.id))
                rt.delete()

    def delete_dhcp_options(self):
        """Delete DHCP Options Set"""
        self.log.emit('deleting DHCP Options set {}'.format(self.dhcp_options.id))
        self.dhcp_options.delete()
        
    def terminate(self):
        """Terminate all resources related to this VPC!"""        
        self.delete_instances()
        self.rds.delete_related_db_instances()
        self.key_pair.delete_key_pairs()
        self.vpc_endpoint.delete_related()
        self.delete_security_groups()
        self.delete_subnets()
        self.delete_route_tables()
        self.delete_internet_gateways()
        self.detach_vpn_gateway()
        self.log.emit('deleting the VPC - {}'.format(self.id))
        self.vpc.delete()
        self.delete_dhcp_options()

