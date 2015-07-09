import boto3

from botoform.util import reflect_attrs

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
        if vpc_name is not None:
            self.init(vpc_name)

    def init(self, vpc_name):
        """Finish init process, attach related Boto3 resources and clients."""
        # instantiate a boto3 ec2 resource object, attach to self.
        self.ec2 = boto3.resource('ec2', region_name = self.region_name)

        self.vpc = self.get_vpc_by_name_tag(vpc_name)

        # reflect all attributes of boto3's vpc resource object into self.
        reflect_attrs(self, self.vpc)

        # attach a bunch of Boto3 resources and clients:
        self.rds = boto3.client('rds', region_name = self.region_name)
        self.elasticache = boto3.client('elasticache', region_name = self.region_name)

    def _get_vpcs_by_filter(self, vpc_filter):
        # external API call to AWS.
        return list(self.ec2.vpcs.filter(Filters=vpc_filter))

    def get_vpc_by_name_tag(self, vpc_name):
        """lookup vpc by vpc_name tag. Raises exceptions on insanity."""
        vpc_name_tag_filter = [{'Name':'tag:Name', 'Values':[vpc_name]}]
        vpcs = self._get_vpcs_by_filter(vpc_name_tag_filter)
        if len(vpcs) > 1:
            raise Exception('Multiple VPCs match tag Name:{}'.format(vpc_name))
        if len(vpcs) == 0:
            raise Exception('VPC not found with tag Name:{}'.format(vpc_name))
        return vpcs[0]

    @property
    def tag_dict(self):
        tags = {}
        for tag in self.tags:
            tags[tag['Key']] = tag['Value']
        return tags

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
        for instance in self.instances:
            if instance.role not in roles:
                roles[instance.role] = []
            roles[instance.role].append(instance)
        return roles

    def get_role(self, role_name):
        """Return a list of EnrichedInstance objects with the given role_name"""
        return self.get_roles()[role_name]

    @staticmethod
    def _set(x):
        """Return a set of the given iterable, return emtpy set if None."""
        return set() if x is None else set(x)

    def _identify_instance(self, i, identifiers, roles):
        return identifiers.intersection(i.identifiers) or i.role in roles

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
            raise Exception(msg.format(', '.join(instances), identifier))
        if len(instances) == 0:
            return None
        return instances[0]

    def find_instances(
          self,
          identifiers = None,
          roles = None,
          exclude_identifiers = None,
          exclude_roles = None
        ):
        """
        Accept optional identifiers, roles, exclude_identifiers, exclude_roles.
        Return a list of instances that qualify.

        Note:
         This method returns no instances if all qualifiers are None.

        Danger:
         If either exclude_identifiers or exclude_roles are not None,
         we could end up returning all instances.
        """
        identifiers = self._set(identifiers)
        roles = self._set(roles)
        exclude_identifiers = self._set(exclude_identifiers)
        exclude_roles = self._set(exclude_roles)
        instances = []
        for i in self.get_instances():
            if self._identify_instance(i, identifiers, roles):
                instances.append(i)
            if len(exclude_identifiers) != 0 or len(exclude_roles) != 0:
                if not self._identify_instance(i, exclude_identifiers, exclude_roles):
                    instances.append(i)
        return instances

    def include_instances(self, identifiers = None, roles = None):
        """
        Accept a list of identifiers and/or roles.
        Return a list of instances which match either qualifier list.

        Note:
         This method returns no instances if both identfiers and roles is None.
        """
        return self.find_instances(identifiers = identifiers, roles = roles)

    def exclude_instances(self, identifiers = None, roles = None):
        """
        Accept a list of identifiers and/or roles.
        Return a list of instances which do *not* match either qualifier list.

        Note:
         This method returns all instances if both identfiers and roles is None.
        """
        return self.find_instances(
                   exclude_identifiers = identifiers,
                   exclude_roles = roles
               )

    @property
    def instances(self): return self.get_instances()

    @property
    def roles(self): return self.get_roles()


