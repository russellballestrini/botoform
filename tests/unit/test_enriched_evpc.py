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
        # TODO: define custom exceptions for botoform.
        with self.assertRaises(Exception):
            self.evpc1.get_vpc_by_name_tag('webapple01')

    def test_get_vpc_by_name_tag_multi_vpcs_error(self):
        # mock the _get_vpcs_by_filter method to return a list with two vpcs.
        self.evpc1._get_vpcs_by_filter = MagicMock(return_value=[1, 2])
        # TODO: define custom exceptions for botoform.
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

    def test_include_instances_identifiers(self):
        web01 = self.evpc1.include_instances(identifiers=['web01'])
        self.assertEqual(len(web01), 1)
        self.assertEqual(web01[0].shortname, 'web01')

        ip_32 = self.evpc1.include_instances(identifiers=['192.168.1.32'])
        self.assertEqual(len(ip_32), 1)
        self.assertEqual(ip_32[0].shortname, 'web02')

        mix = self.evpc1.include_instances(identifiers=['web02', 'proxy01'])
        self.assertEqual(len(mix), 2)

    def test_include_instances_roles(self):
        proxy = self.evpc1.include_instances(roles=['proxy'])
        self.assertEqual(len(proxy), 1)

        web   = self.evpc1.include_instances(roles=['web'])
        self.assertEqual(len(web), 2)

    def test_include_instances_identifiers_and_roles(self):
        mix = self.evpc1.include_instances(
                                   identifiers=['web02'],
                                   roles=['proxy']
                                 )
        self.assertEqual(len(mix), 2)

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

    def test_find_instance(self):
        web01 = self.evpc1.find_instance('web01')
        web02 = self.evpc1.find_instance('192.168.1.32')
        proxy01 = self.evpc1.find_instance('webapp01-proxy01')
        taco01 = self.evpc1.find_instance('taco')

        self.assertEqual(web01.hostname, 'webapp01-web01')
        self.assertEqual(web02.hostname, 'webapp01-web02')
        self.assertEqual(proxy01.hostname, 'webapp01-proxy01')
        self.assertEqual(taco01, None)

    def test_find_instance_multi_exception(self):
        # cause two instances to match 'web01' identifier.
        self.evpc1.get_instances = MagicMock(
                                     return_value = [
                                       self.instance1,
                                       self.instance1b,
                                     ]
                                   )
        # TODO: define custom exceptions for botoform.
        with self.assertRaises(Exception):
            web01 = self.evpc1.find_instance('web01')


