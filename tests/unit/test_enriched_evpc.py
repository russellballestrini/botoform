from helpers import BotoformTestCase

class TestEnrichedVPC(BotoformTestCase):

    def test_get_vpc_by_name_tag(self):
        # mock the _get_vpcs_by_filter method to return a list with one vpc.
        self.evpc1._get_vpcs_by_filter = lambda x : [1]
        self.evpc1.get_vpc_by_name_tag('webapp01')

    def test_get_vpc_by_name_tag_no_vpc_error(self):
        # mock the _get_vpcs_by_filter method to return an empty list.
        self.evpc1._get_vpcs_by_filter = lambda x : []
        with self.assertRaises(Exception):
            self.evpc1.get_vpc_by_name_tag('webapple01')

    def test_get_vpc_by_name_tag_multi_vpcs_error(self):
        # mock the _get_vpcs_by_filter method to return a list with two vpcs.
        self.evpc1._get_vpcs_by_filter = lambda x : [1, 2]
        with self.assertRaises(Exception):
            self.evpc1.get_vpc_by_name_tag('webapp*')


