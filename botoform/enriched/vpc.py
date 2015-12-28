from botoform.util import (
  BotoConnections,
  reflect_attrs,
  make_tag_dict,
  make_filter,
  name_tag_filter,
)

from instance import EnrichedInstance
from vpc_endpoint import EnrichedVpcEndpoint
from elasticache import EnrichedElastiCache
from elb import EnrichedElb

from nested_lookup import nested_lookup

class EnrichedVPC(object):
    """
    This class uses composition to enrich Boto3's VPC resource class.
    Here we relate AWS resources using various techniques like the vpc_name tag.
    We also provide methods for managing the lifecycle of related AWS resources.
    """

    def __init__(self, vpc_name=None, region_name=None, profile_name=None):
        self.boto = BotoConnections(region_name, profile_name)
        if vpc_name is not None:
            self.connect(vpc_name)
        self.vpc_endpoint = EnrichedVpcEndpoint(self)
        self.elasticache = EnrichedElastiCache(self)
        self.elb = EnrichedElb(self)

    def _get_vpcs_by_filter(self, vpc_filter):
        # external API call to AWS.
        return list(self.boto.ec2.vpcs.filter(Filters=vpc_filter))

    def get_vpc_by_name_tag(self, vpc_name):
        """lookup vpc by vpc_name tag. Raises exceptions on insanity."""
        vpcs = self._get_vpcs_by_filter(name_tag_filter(vpc_name))
        if len(vpcs) > 1:
            raise Exception('Multiple VPCs match tag Name:{}'.format(vpc_name))
        if len(vpcs) == 0:
            raise Exception('VPC not found with tag Name:{}'.format(vpc_name))
        return vpcs[0]

    def connect(self, vpc_name):
        """connect to VPC and reflect all attributes into self."""
        self.vpc = self.get_vpc_by_name_tag(vpc_name)
        # reflect all attributes of boto3's vpc resource object into self.
        reflect_attrs(self, self.vpc)

    @property
    def tag_dict(self):
        return make_tag_dict(self)

    @property
    def name(self): return self.tag_dict.get('Name', None)

    @property
    def region_name(self): return self.boto.region_name

    @property
    def azones(self): return self.boto.azones

    @property
    def identity(self): return self.name or self.id

    def __str__(self): return self.identity

    def ec2_to_enriched_instances(self, ec2_instances):
        """Convert list of boto.ec2.instance.Instance to EnrichedInstance"""
        return [EnrichedInstance(e, self) for e in ec2_instances]

    def _ec2_instances(self):
        # external API call to AWS.
        return self.vpc.instances.all()

    def get_instances(self):
        """Return a list of each EnrichedInstance object related to this VPC."""
        return self.ec2_to_enriched_instances(self._ec2_instances())

    def get_running_instances(self):
        """Return list running EnrichedInstance object related to this VPC."""
        return [i for i in self.get_instances() if i.state['Code'] == 16]

    def get_roles(self):
        """
        Return a dict of lists where role is the key and
        a list of EnrichedInstance objects is the value.
        """
        roles = {}
        for instance in self.get_instances():
            if instance.role not in roles:
                roles[instance.role] = []
            roles[instance.role].append(instance)
        return roles

    def get_role(self, role_name):
        """Return a list of EnrichedInstance objects with the given role_name"""
        return self.get_roles()[role_name]

    def find_instance(self, identifier):
        """
        Given an identifier, return an instance or None.
        Raises exception if multiple instances match identifier.
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

        identifiers:
          A list of identifiers to qualify instances by, for example:
            * custid-ui01
            * ui01
            * 192.168.1.9
            * i-01234567

        roles:
          A list of roles to qualify instances by, for example:
            * ui
            * api
            * proxy

        exclude:
          If True, qualifiers exclude instead of include!
          Defaults to False.

        Danger:
          This method will return *no* instances if all qualifiers are None.
          However, if *exclude* is True we could return *all* instances!
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
        objs = list(collection.filter(Filters=name_tag_filter(names)))
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

    def associate_route_table_with_subnet(self, rt_name, sn_name):
        """Accept a route table name and subnet name, associate them."""
        self.boto.ec2_client.associate_route_table(
                        RouteTableId = self.get_route_table(rt_name).id,
                        SubnetId     = self.get_subnet(sn_name).id,
        )

    def delete_internet_gateways(self):
        """Delete related internet gatways."""
        for igw in self.internet_gateways.all():
            igw.detach_from_vpc(VpcId = self.id)
            igw.delete()

    def delete_security_groups(self):
        """Delete related security groups."""
        for sg in self.security_groups.all():
            if len(sg.ip_permissions) >= 1:
                sg.revoke_ingress(IpPermissions = sg.ip_permissions)

        for sg in self.security_groups.all():
            if sg.group_name == 'default':
                continue
            sg.delete()

    def delete_subnets(self):
        """Delete related subnets."""
        for sn in self.subnets.all():
            sn.delete()

    def delete_route_tables(self):
        """Delete related route tables."""
        main_rt = self.get_main_route_table()
        for rt in self.route_tables.all():
            if rt.id != main_rt.id:
                for a in rt.associations.all():
                    a.delete()
                rt.delete()

    def terminate(self):
        """Terminate all resources related to this VPC!"""
        self.vpc_endpoint.delete_related()
        self.delete_security_groups()
        self.delete_subnets()
        self.delete_route_tables()
        self.delete_internet_gateways()
        self.vpc.delete()

