import re

from botoform.util import reflect_attrs

class EnrichedInstance(object):
    """
    This class uses composition to enrich Boto3's ec2.Instance resource class.
    """

    def __init__(self, instance, vpc=None):
        """Composted ec2.Instance(boto3.resources.base.ServiceResource) class"""
        if vpc is not None:
            self.vpc = vpc
        self.instance = instance
        # reflect all attributes of ec2.Instance into self.
        reflect_attrs(self, self.instance)

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

    @property
    def tag_dict(self):
        tags = {}
        for tag in self.tags:
            tags[tag['Key']] = tag['Value']
        return tags

    @property
    def hostname(self):
        return self.tag_dict.get('Name', None)

    @property
    def identity(self): return self.hostname or self.id

    def _regex_hostname(self, regex):
        if self.hostname is None:
            return None
        match = re.match(regex, self.hostname)
        if match is None:
            raise Exception(
              "Invalid Name=%s tag, custid-<role>NN" % (self.hostname)
            )
        return match.group(1)

    @property
    def shortname(self):
        """get shortname from instance Name tag, ex: proxy02, web01, ..."""
        return self._regex_hostname(r".*?-(.*)$")

    @property
    def role(self):
        """get role from instance Name tag, ex: api, vpn, ..."""
        #if self.is_autoscale:
        #    return self.autoscale_groupname.split('-')[-1]
        return self._regex_hostname(r".*?-(.*?)\d+$")

    @property
    def identifiers(self):
        """Return a tuple of "unique" identifier strings for instance."""
        _identifiers = (self.hostname, self.shortname, self.id,
                       self.private_ip_address, self.public_ip_address)
        return tuple([x for x in _identifiers if x is not None])


