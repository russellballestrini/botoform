import re

from botoform.util import (
  reflect_attrs,
  make_tag_dict,
  id_to_human,
)

class EnrichedInstance(object):
    """
    This class uses composition to enrich Boto3's Instance resource class.

    ec2.Instance(boto3.resources.base.ServiceResource)

    Reference:

    https://boto3.readthedocs.org/en/latest/reference/services/ec2.html#instance
    """

    def __init__(self, instance, evpc=None):
        """
        EnrichedInstance Resource.
        
        :param instance: ec2.Instance(boto3.resources.base.ServiceResource)
        :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`
        
        """
        if evpc is not None:
            self.evpc = evpc

        self.instance = instance

        # capture a list of this classes attributes before reflecting.
        self.self_attrs = dir(self)

        # reflect all attributes of ec2.Instance into self.
        self.reflect_attrs()

    def __eq__(self, other):
        """Determine if equal by instance id"""
        return self.id == other.id

    def __ne__(self, other):
        """Determine if not equal by instance id"""
        return (not self.__eq__(other))

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.identity

    def reflect_attrs(self):
        """reflect all attributes of ec2.Instance into self."""
        reflect_attrs(self, self.instance, skip_attrs=self.self_attrs)

    def reload(self):
        """run the reload method on the attached instance and reflect_attrs."""
        self.instance.reload()
        self.reflect_attrs()

    @property
    def tag_dict(self):
        """Return dictionary of tags."""
        return make_tag_dict(self.instance)

    @property
    def hostname(self):
        """Return hostname (AWS Name tag)."""
        return self.tag_dict.get('Name', None)

    @property
    def name(self):
        """Return hostname (AWS Name tag)."""
        return self.hostname

    @property
    def identity(self):
        """Return hostname (AWS Name tag) or id."""
        return self.hostname or self.id

    @property
    def id_human(self):
        """Return humanhash of id."""
        return id_to_human(self.id)

    def _regex_hostname(self, regex):
        if self.hostname is None:
            return None
        match = re.match(regex, self.hostname)
        if match is None:
            return None
        return match.group(1)

    @property
    def shortname(self):
        """Return shortname from hostname: web-solarmaine, db-beerindia, ..."""
        return self._regex_hostname(r".*?-(.*)$")

    @property
    def role(self):
        """Return role from from 'role' or 'Name' tag: web, db, ..."""
        role = self.tag_dict.get('role', None)
        if role is None:
            role = self._regex_hostname(r".*?-(.*?)-.+$")
        if role is None:
            role = self._regex_hostname(r".*?-(.*?)-?\d+$")
        return role

    @property
    def identifiers(self):
        """
        Return a tuple of "unique" identifier strings for instance.
        :rtype: tuple 
        """
        _identifiers = (self.hostname, self.shortname,
                       self.id, self.id_human,
                       self.private_ip_address, self.public_ip_address)
        return tuple([x for x in _identifiers if x is not None])

    @property
    def autoscale_group(self):
        """Return autoscaling group name (AWS aws:autoscaling:groupName tag)."""
        return self.tag_dict.get('aws:autoscaling:groupName', None)

    @property
    def is_autoscaled(self):
        """Return True if this instance was autoscaled else False"""
        return False if self.autoscale_group is None else True

    def disable_source_dest_check(self, boolean):
        self.modify_attribute(SourceDestCheck={'Value':boolean})

    def disable_api_termination(self, boolean):
        self.modify_attribute(DisableApiTermination={'Value':boolean})

    def lock(self):
        """Lock this instance to prevent termination."""
        self.disable_api_termination(True)

    def unlock(self):
        """Unlock this instance to allow termination."""
        self.disable_api_termination(False)

    @property
    def eips(self):
        """
        Return a list of VpcAddress objects associated to this instance.
        :rtype: list
        """
        instance_id_filter = [{'Name':'instance-id', 'Values':[self.id]}]
        address_descriptions = self.evpc.boto.ec2_client.describe_addresses(
                                   Filters = instance_id_filter
                               )['Addresses']
        addresses = []
        for address_description in address_descriptions:
            addresses.append(
                self.evpc.boto.ec2.VpcAddress(
                    address_description['AllocationId']
                )
            )
        return addresses

    def wait_until_status_ok(self):
        """Wait (block) until this instance state is 'OK'."""
        waiter = self.evpc.boto.ec2_client.get_waiter('instance_status_ok')
        waiter.wait(InstanceIds=[self.id])
        # once 'OK' reload to in sure autoscaled instances have tags applied.
        self.reload()

    def allocate_eip(self):
        """
        Allocate a new EIP and associate with this instance.

        :returns: New VpcAddress EIP object
        """
        self.wait_until_running()
        allocation = self.evpc.boto.ec2_client.allocate_address()
        eip = self.evpc.boto.ec2.VpcAddress(
                                     allocation_id = allocation['AllocationId']
                                 )
        eip.associate(InstanceId = self.id)
        self.reload()
        return eip

    def disassociate_eips(self, release=True):
        """
        Disassociate all EIPs associated with this instance.

        :param release: Also release allocations for EIPs. Default True.

        :rtype: None
        """
        for eip in self.eips:
            eip.association.delete()
            if release is True:
                eip.release()
        self.reload()

