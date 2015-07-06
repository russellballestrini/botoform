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

    def test_instances(self):
        self.assertEqual(len(self.evpc1.instances), 2)

    def test_roles(self):
        self.assertEqual(len(self.evpc1.roles), 2)

    def test_get_role(self):
        role_web   = self.evpc1.get_role('web')
        role_proxy = self.evpc1.get_role('proxy')
        self.assertEqual(len(role_web), 1)
        self.assertEqual(len(role_proxy), 1)
        self.assertEqual(role_web[0].hostname, 'webapp01-web01')
        self.assertEqual(role_proxy[0].hostname, 'webapp01-proxy02')

    def test_get_role_missing_is_key_error(self):
        with self.assertRaises(KeyError):
            self.evpc1.get_role('taco')


