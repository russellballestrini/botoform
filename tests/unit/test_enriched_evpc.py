from unittest import TestCase

from mock import Mock

from botoform.evpc import EnrichedVPC

class TestEnrichedVPC(TestCase):
    def setUp(self):
        pass

    def test_get_vpc_by_name_tag(self):
        # mock the self.ec2.vpcs.filter method to return a list with one vpc.

    def test_get_vpc_by_name_tag_no_vpc_error(self):
        # mock the self.ec2.vpcs.filter method to return an empty list.
        pass

    def test_get_vpc_by_name_tag_multi_vpcs_error(self):
        # mock the self.ec2.vpcs.filter method to return two vpcs.
        pass
