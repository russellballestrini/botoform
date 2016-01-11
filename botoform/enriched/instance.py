import re

from botoform.util import (
  reflect_attrs,
  make_tag_dict,
)

class EnrichedInstance(object):
    """
    This class uses composition to enrich Boto3's ec2.Instance resource class.
    """

    def __init__(self, instance, evpc=None):
        """Composted ec2.Instance(boto3.resources.base.ServiceResource) class"""
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
        return make_tag_dict(self.instance)

    @property
    def hostname(self):
        return self.tag_dict.get('Name', None)

    @property
    def name(self):
        return self.hostname

    @property
    def identity(self): return self.hostname or self.id

    def _regex_hostname(self, regex):
        if self.hostname is None:
            return None
        match = re.match(regex, self.hostname)
        if match is None:
            return None
        return match.group(1)

    @property
    def shortname(self):
        """get shortname from instance Name tag, ex: proxy02, web01, ..."""
        return self._regex_hostname(r".*?-(.*)$")

    @property
    def role(self):
        """get role from instance 'role' or 'Name' tag, ex: api, vpn, ..."""
        role = self.tag_dict.get('role', None)
        if role is None:
             role = self._regex_hostname(r".*?-(.*?)-.+$")
        if role is None:
             role = self._regex_hostname(r".*?-(.*?)-?\d+$")
        return role

    @property
    def identifiers(self):
        """Return a tuple of "unique" identifier strings for instance."""
        _identifiers = (self.hostname, self.shortname, self.id,
                       self.private_ip_address, self.public_ip_address)
        return tuple([x for x in _identifiers if x is not None])

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
        """Return a list of VpcAddress objects associated to this instance."""
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
        for eip in self.eips:
            eip.association.delete()
            if release is True:
                eip.release()
        self.reload()

