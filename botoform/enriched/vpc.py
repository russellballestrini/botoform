from botoform.util import (
  BotoConnections,
  Log,
  reflect_attrs,
  make_tag_dict,
  make_filter,
  tag_filter,
  write_private_key,
  update_tags,
  collection_to_list,
)

from instance import EnrichedInstance
from vpc_endpoint import EnrichedVpcEndpoint
from autoscaling import EnrichedAutoscaling
from elasticache import EnrichedElastiCache
from elb import EnrichedElb
from rds import EnrichedRds
from key_pair import EnrichedKeyPair
from route53 import EnrichedRoute53

from enriched import (
  Enriched,
  EnrichedRouteTable,
  EnrichedSubnet,
  EnrichedSecurityGroup,
)

from nested_lookup import nested_lookup

from retrying import retry

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
        self.route53 = EnrichedRoute53(self)

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

    def get_autoscaled_instances(self, instances=None):
        """return a list of instances which were created via autoscaling."""
        instances = self.get_instances(instances)
        return [instance for instance in instances if instance.is_autoscaled == True]

    def get_normal_instances(self, instances=None):
        """return a list of instances which were _not_ created via autoscaling."""
        instances = self.get_instances(instances)
        return [instance for instance in instances if instance.is_autoscaled == False]

    def get_running_instances(self, instances=None):
        """Return list running EnrichedInstance object related to this VPC."""
        instances = self.get_instances(instances)
        return [instance for instance in instances if instance.state['Code'] == 16]

    def get_roles(self, instances=None):
        """
        Return a dict of lists where role is the key and
        a list of EnrichedInstance objects is the value.
        """
        roles = {}
        instances = self.get_instances(instances)
        for instance in instances:
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
        instances = self.get_instances()
        hits = []
        for instance in instances:
            if identifier in instance.identifiers:
                hits.append(instance)

        if len(hits) == 0:
            return None

        if len(hits) > 1:
            msg = "Multiple instances '{}' have '{}' identifier."
            instance_names = ', '.join(map(str, hits))
            raise Exception(msg.format(instance_names, identifier))

        return hits[0]

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
        instances = self.get_instances()
        hits = []
        for i in instances:
            qualified = self._identify_instance(i, identifiers, roles)
            if qualified and exclude == False:
                hits.append(i)
            elif not qualified and exclude == True:
                hits.append(i)
        return hits

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
            for association in route_table.associations:
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
        ec2_object = self._filter_collection_by_name(name, self.route_tables)
        if ec2_object is not None:
            return EnrichedRouteTable(ec2_object, evpc=self)

    def get_subnet(self, name):
        """Accept subnet name, return subnet object or None."""
        ec2_object = self._filter_collection_by_name(name, self.subnets)
        if ec2_object is not None:
            return EnrichedSubnet(ec2_object, evpc=self)

    def get_security_group(self, name):
        """Accept security group name, return security group object or None."""
        ec2_object = self._filter_collection_by_name(name, self.security_groups)
        if ec2_object is not None:
            return EnrichedSecurityGroup(ec2_object, evpc=self)

    def associate_route_table_with_subnet(self, rt_name, sn_name):
        """Accept a route table name and subnet name, associate them."""
        self.boto.ec2_client.associate_route_table(
                        RouteTableId = self.get_route_table(rt_name).id,
                        SubnetId     = self.get_subnet(sn_name).id,
        )

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

    def lock_instances(self, instances=None):
        """Lock all or a list of instances."""
        instances = self.get_instances(instances)
        for instance in instances:
            instance.lock()

    def unlock_instances(self, instances=None):
        """Unlock all or a list of instances."""
        instances = self.get_instances(instances)
        for instance in instances:
            instance.unlock()

    def get_vgw(self, vgw_id):
        """Accept vgw_id and return vgw description."""
        return self.boto.ec2_client.describe_vpn_gateways(VpnGatewayIds=[vgw_id])

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def ensure_vgw_state(vgw_id, desired_state='attached'):
        """if vgw is not in expected state, throw exception."""
        vgw = self.get_vgw(vgw_id)
        self.log.emit('waiting for {} to become {}'.format(vgw_id, desired_state), 'debug')
        # Janky: this if statement is terrible... but I don't know the structure.
        if vgw.get('VpnGateways')[0].get('VpcAttachments')[0].get('State') != desired_state:
            raise Exception('{} not in {} desired_State'.format(vgw_id, desired_state))

    def attach_vpn_gateway(self, vgw_id):
        """Attach VPN gateway to the VPC"""
        self.log.emit('attaching vgw {} to vpc {}'.format(vgw_id, self.vpc_name))
        self.boto.ec2_client.attach_vpn_gateway(
                    DryRun=False,
                    VpnGatewayId = vgw_id,
                    VpcId = self.id,                                    
                )
        self.ensure_vgw_state(vgw_id, 'attached')
     
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
            self.ensure_vgw_state(vgw_id, 'detached')

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

    def revoke_inbound_rules_from_sg(self, sg):
        if len(sg.ip_permissions) >= 1:
            self.log.emit('revoking all inbound rules of security group - {}'.format(sg.id))
            sg.revoke_ingress(IpPermissions = sg.ip_permissions)

    def revoke_outbound_rules_from_sg(self, sg):
        if len(sg.ip_permissions_egress) >= 1:
            self.log.emit('revoking all outbound rules of security group - {}'.format(sg.id))
            sg.revoke_egress(IpPermissions = sg.ip_permissions_egress)

    def revoke_security_group_rules(self, sg):
        self.revoke_inbound_rules_from_sg(sg)
        self.revoke_outbound_rules_from_sg(sg)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def delete_security_group(self, sg):
        if sg.group_name != 'default':
            self.log.emit('deleting security group - {}'.format(sg.id))
            sg.delete()

    def delete_security_groups(self):
        """Delete related security groups."""
        sgs = self.security_groups.all()
        for sg in sgs:
            self.revoke_security_group_rules(sg)

        for sg in sgs:
            self.delete_security_group(sg)

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
                for a in rt.associations:
                    self.log.emit('dissociating subnet {} from route table {}'.format(a.subnet_id, a.route_table_id))
                    a.delete()
                self.log.emit('deleting route table {}'.format(rt.id))
                rt.delete()

    def delete_dhcp_options(self):
        """Delete DHCP Options Set"""
        msg = 'deleting DHCP Options set {}'
        self.log.emit(msg.format(self.dhcp_options.id))
        self.dhcp_options.delete()
        
    def terminate(self):
        """Terminate all resources related to this VPC!"""        
        autoscaled_instances = self.get_autoscaled_instances()
        self.delete_instances(self.get_normal_instances())
        self.elb.delete_related_elbs()
        self.autoscaling.delete_related_autoscaling_groups()
        self.autoscaling.delete_related_launch_configs()
        self.rds.delete_related_db_instances()
        self.key_pair.delete_key_pairs()
        self.vpc_endpoint.delete_related()
        self.wait_until_instances(instances=autoscaled_instances, state='terminated')
        self.delete_security_groups()
        self.delete_subnets()
        self.delete_route_tables()
        self.delete_internet_gateways()
        self.detach_vpn_gateway()
        self.route53.delete_private_zone()
        self.log.emit('deleting the VPC - {}'.format(self.id))
        self.vpc.delete()
        self.delete_dhcp_options()

    def _strip_vpc_name(self, string):
        return string[len(self.vpc_name)+1:] if string.startswith(self.vpc_name+'-') else string

    def _permission_to_rules(self, perm):
        rules = []
        ip_protocol = perm['IpProtocol']
        from_port = perm.get('FromPort', -1)
        to_port   = perm.get('ToPort', -1)
        port_range = from_port
        if from_port != to_port:
            port_range = '{}-{}'.format(from_port, to_port)
        if len(perm['IpRanges']) >= 1:
            for iprange in perm['IpRanges']:
                rule = []
                rule.append(iprange['CidrIp'])
                rule.append(ip_protocol)
                rule.append(port_range)
                rules.append(tuple(rule))
        if len(perm['UserIdGroupPairs']) >= 1:
            for pair in perm['UserIdGroupPairs']:
                rule = []
                related_sg = self.boto.ec2.SecurityGroup(id=pair['GroupId'])
                related_sg_name = self._strip_vpc_name(related_sg.group_name)
                rule.append(related_sg_name)
                rule.append(ip_protocol)
                rule.append(port_range)
                rules.append(tuple(rule))
        return rules

    @property
    def enriched_security_groups(self):
        """
        Format Security Groups (and permissions) in :ref:`Botoform Schema <schema reference>`.

        :returns: security_groups in :ref:`Botoform Schema <schema reference>`.
        """
        sgs = {}
        for sg in self.security_groups.all():
            sg_name = self._strip_vpc_name(sg.group_name)
            sgs[sg_name] = {'inbound' : []}
            for perm in sg.ip_permissions:
                rules = self._permission_to_rules(perm)
                sgs[sg_name]['inbound'] += rules

            for perm in sg.ip_permissions_egress:
                # only add outbound rules if not the default rule.
                rules = self._permission_to_rules(perm)
                if len(rules) == 1 and rules[0] == ('0.0.0.0/0', '-1', -1):
                    continue
                if 'outbound' not in sgs[sg_name]:
                    sgs[sg_name]['outbound'] = []
                sgs[sg_name]['outbound'] += rules

        return sgs

    @property
    def taggable_resources(self):
        """Return a list of taggable objects related to this VPC."""
        instances = self.instances
        resources = [self, self.dhcp_options]
        resources += instances
        for instance in instances:
            resources += collection_to_list(instance.volumes)
        resources += collection_to_list(self.internet_gateways)
        resources += collection_to_list(self.subnets)
        resources += collection_to_list(self.security_groups)
        resources += collection_to_list(self.route_tables)
        return resources


