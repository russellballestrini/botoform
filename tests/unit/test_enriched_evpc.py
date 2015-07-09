from helpers import BotoformTestCase

from mock import MagicMock

class TestEnrichedVPC(BotoformTestCase):

    def test_get_vpc_by_name_tag(self):
        # mock the _get_vpcs_by_filter method to return a list with one vpc.
        self.evpc1._get_vpcs_by_filter = MagicMock(return_value=[1])
        self.evpc1.get_vpc_by_name_tag('webapp01')

    def test_get_vpc_by_name_tag_no_vpc_error(self):
        # mock the _get_vpcs_by_filter method to return an empty list.
        self.evpc1._get_vpcs_by_filter = MagicMock(return_value=[])
        with self.assertRaises(Exception):
            self.evpc1.get_vpc_by_name_tag('webapple01')

    def test_get_vpc_by_name_tag_multi_vpcs_error(self):
        # mock the _get_vpcs_by_filter method to return a list with two vpcs.
        self.evpc1._get_vpcs_by_filter = MagicMock(return_value=[1, 2])
        with self.assertRaises(Exception):
            self.evpc1.get_vpc_by_name_tag('webapp*')

    def test_instances(self):
        self.assertEqual(len(self.evpc1.instances), 3)

    def test_roles(self):
        self.assertEqual(len(self.evpc1.roles), 2)

    def test_get_role(self):
        role_web   = self.evpc1.get_role('web')
        role_proxy = self.evpc1.get_role('proxy')
        self.assertEqual(len(role_web), 2)
        self.assertEqual(len(role_proxy), 1)
        self.assertIn('web', role_web[0].hostname)
        self.assertIn('web', role_web[1].hostname)
        self.assertEqual(role_proxy[0].hostname, 'webapp01-proxy01')

    def test_get_role_missing_is_key_error(self):
        with self.assertRaises(KeyError):
            self.evpc1.get_role('taco')

    def test_exclude_instances_identifiers(self):
        without_web01 = self.evpc1.exclude_instances(identifiers=['web01'])
        self.assertEqual(len(without_web01), 2)

        without_ip = self.evpc1.exclude_instances(identifiers=['192.168.1.32'])
        self.assertEqual(len(without_ip), 2)

        without_mix = self.evpc1.exclude_instances(
                                   identifiers=['web02', 'proxy01'])
        self.assertEqual(len(without_mix), 1)
        self.assertEqual(without_mix[0].shortname, 'web01')

    def test_exclude_instances_roles(self):
        without_proxy = self.evpc1.exclude_instances(roles=['proxy'])
        self.assertEqual(len(without_proxy), 2)

        without_web   = self.evpc1.exclude_instances(roles=['web'])
        self.assertEqual(len(without_web), 1)

    def test_exclude_instances_identifiers_and_roles(self):
        without_mix = self.evpc1.exclude_instances(
                                   identifiers=['web02'],
                                   roles=['proxy']
                                 )
        self.assertEqual(len(without_mix), 1)
        self.assertEqual(without_mix[0].shortname, 'web01')


