from botoform.util import (
  BotoConnections,
  reflect_attrs,
  make_tag_dict,
)

from instance import EnrichedInstance

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

    def _get_vpcs_by_filter(self, vpc_filter):
        # external API call to AWS.
        return list(self.boto.ec2.vpcs.filter(Filters=vpc_filter))

    def get_vpc_by_name_tag(self, vpc_name):
        """lookup vpc by vpc_name tag. Raises exceptions on insanity."""
        vpc_name_tag_filter = [{'Name':'tag:Name', 'Values':[vpc_name]}]
        vpcs = self._get_vpcs_by_filter(vpc_name_tag_filter)
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
    def identity(self): return self.name or self.id

    def __str__(self): return self.identity

    def ec2_to_enriched_instances(self, ec2_instances):
        """Convert list of boto.ec2.instance.Instance to EnrichedInstance"""
        return [EnrichedInstance(e, self) for e in ec2_instances]

    def _ec2_instances(self):
        # external API call to AWS.
        return list(self.vpc.instances.all())

    def get_instances(self):
        """Return a list of each EnrichedInstance object related to this VPC."""
        return self.ec2_to_enriched_instances(self._ec2_instances())

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
        for route_table in list(self.route_tables.all()):
            for association in list(route_table.associations.all()):
                if association.main == True:
                    main_route_table.append(route_table)
        if len(main_route_table) != 1:
            raise Exception('cannot get main route table! {}'.format(main_route_table))
        return main_route_table[0]

