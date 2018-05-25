from botoform.util import reflect_attrs, make_tag_dict, id_to_human


class Enriched(object):
    """
    This class uses composition to enrich Boto3's "ec2_object" classes.

    This class provides additional "helper" methods and attributes.
    """

    def __init__(self, ec2_object, evpc=None):
        """
        :param ec2_object: an object with tags 
        :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`
        """
        if evpc is not None:
            self.evpc = evpc

        self.ec2_object = ec2_object

        # capture a list of this classes attributes before reflecting.
        self.self_attrs = dir(self)

        # reflect all attributes of ec2_object into self.
        self.reflect_attrs()

    def __eq__(self, other):
        """Determine if equal by id"""
        return self.id == other.id

    def __ne__(self, other):
        """Determine if not equal by id"""
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.identity

    def reflect_attrs(self):
        """reflect all attributes of ec2_object into self."""
        reflect_attrs(self, self.ec2_object, skip_attrs=self.self_attrs)

    def reload(self):
        """run the reload method on the attached ec2_object and reflect_attrs."""
        self.ec2_object.reload()
        self.reflect_attrs()

    @property
    def tag_dict(self):
        """Return dictionary of tags."""
        return make_tag_dict(self.ec2_object)

    @property
    def name(self):
        """Return name (AWS Name tag)."""
        return self.tag_dict.get("Name", None)

    @property
    def identity(self):
        """Return name (AWS Name tag) or id."""
        return self.name or self.id

    @property
    def id_human(self):
        """Return humanhash of id."""
        return id_to_human(self.id)


class EnrichedRouteTable(Enriched):
    pass


class EnrichedSubnet(Enriched):
    pass


class EnrichedSecurityGroup(Enriched):
    pass
